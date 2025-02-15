from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, MessageGraph, START, END
from langchain_groq import ChatGroq
import asyncio
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Data structures
@dataclass
class Slide:
    index: int
    title: str
    content_type: str  # "text", "mermaid", "d3"
    content: str
    layout: str

@dataclass
class PresentationState:
    topic: str
    description: str
    num_slides: int
    slides: List[Slide]
    current_state: str  # "planning", "generating", "combining"

# Pydantic model for structured output
class SlidePlan(BaseModel):
    index: int = Field(..., description="The index of the slide")
    title: str = Field(..., description="The title of the slide")
    content_type: str = Field(..., description="The type of content (text, mermaid, d3)")
    layout: str = Field(..., description="The layout of the slide")

class PresentationPlan(BaseModel):
    slides: List[SlidePlan] = Field(..., description="List of slides in the presentation")

# Agent definitions
class PresentationPlanner:
    def __init__(self, model="qwen-2.5-coder-32b"):
        self.llm = ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def plan_presentation(self, state: PresentationState) -> PresentationState:
        prompt = f"""
        Create a detailed slide layout plan for a presentation on {state.topic}.
        Description: {state.description}
        Number of slides: {state.num_slides}

        For each slide, provide:
        1. Slide title
        2. Content type (text, mermaid diagram, or d3 visualization)
        3. Brief description of what should be included
        4. Layout suggestions

        Format your response as JSON with the following structure:
        {{
            "slides": [
                {{
                    "index": 0,
                    "title": "string",
                    "content_type": "string",
                    "layout": "string"
                }}
            ]
        }}
        """
        
        # Use the LLM to generate structured output
        response = await self.llm.ainvoke(
            [SystemMessage(content="You are a presentation planning expert."),
             HumanMessage(content=prompt)]
        )
        
        try:
            # Parse the response into the PresentationPlan model
            plan = PresentationPlan.parse_raw(response.content)
            state.slides = [Slide(**slide.dict(), content="") for slide in plan.slides]
            state.current_state = "generating"
        except Exception as e:
            raise ValueError(f"Invalid response from LLM: {e}")
            
        return state

class SlideGenerator:
    def __init__(self, model="qwen-2.5-coder-32b"):
        self.llm = ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def generate_slide(self, slide: Slide, topic: str) -> Slide:
        prompt = f"""
        Generate content for a presentation slide about {topic}.
        Slide title: {slide.title}
        Content type: {slide.content_type}
        Layout: {slide.layout}

        If content_type is "mermaid", create a mermaid.js diagram.
        If content_type is "d3", create a D3.js visualization code.
        If content_type is "text", create formatted HTML content.

        Return only the content code without any explanation.
        """
        
        response = await self.llm.ainvoke(
            [SystemMessage(content="You are a presentation content expert."),
             HumanMessage(content=prompt)]
        )
        
        slide.content = response.content
        return slide

class PresentationCombiner:
    def combine_slides(self, slides: List[Slide]) -> str:
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Generated Presentation</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/white.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
        </head>
        <body>
            <div class="reveal">
                <div class="slides">
                    {slide_content}
                </div>
            </div>
            <script>
                Reveal.initialize({{
                    controls: true,
                    progress: true,
                    center: true,
                    hash: true
                }});
                
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default'
                }});
            </script>
        </body>
        </html>
        """
        
        slide_sections = []
        for slide in slides:
            if slide.content_type == "mermaid":
                content = f'<div class="mermaid">{slide.content}</div>'
            elif slide.content_type == "d3":
                content = f'<div id="d3-{slide.index}" class="d3-container"></div><script>{slide.content}</script>'
            else:
                content = slide.content
                
            slide_sections.append(f'<section><h2>{slide.title}</h2>{content}</section>')
        
        return html_template.format(slide_content="\n".join(slide_sections))

# LangGraph setup
async def create_presentation_graph():
    # Initialize components
    planner = PresentationPlanner()
    generator = SlideGenerator()
    combiner = PresentationCombiner()
    
    # Define graph nodes
    async def plan_node(state: PresentationState) -> PresentationState:
        return await planner.plan_presentation(state)
    
    async def generate_node(state: PresentationState) -> PresentationState:
        # Generate slides concurrently
        tasks = [
            generator.generate_slide(slide, state.topic)
            for slide in state.slides
        ]
        state.slides = await asyncio.gather(*tasks)
        state.current_state = "combining"
        return state
    
    def combine_node(state: PresentationState) -> str:
        return combiner.combine_slides(state.slides)
    
    # Create graph
    workflow = Graph()

    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("combine", combine_node)
    
    # Add edges with START
    workflow.add_edge(START, 'plan')  # Add START to plan edge
    workflow.add_edge("plan", "generate")
    workflow.add_edge("generate", "combine")
    workflow.add_edge("combine", END)  # Add edge from combine to END

    return workflow.compile()

# Usage example
async def generate_presentation(topic: str, description: str, num_slides: Optional[int] = None):
    if num_slides is None:
        # Ask for number of slides using Groq
        llm = ChatGroq(
            model="qwen-2.5-coder-32b",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        response = await llm.ainvoke(
            [SystemMessage(content="You are a presentation expert."),
             HumanMessage(content=f"How many slides would be appropriate for a presentation about {topic}? Return only a number.")]
        )
        num_slides = int(response.content.strip())
    
    # Initialize state
    state = PresentationState(
        topic=topic,
        description=description,
        num_slides=num_slides,
        slides=[],
        current_state="planning"
    )
    
    # Create and run graph
    graph = await create_presentation_graph()
    result = await graph.ainvoke(state)
    print(result)
    
    # Save result to file
    with open("presentation.html", "w") as f:
        f.write(result)
    
    return result

# Example usage
if __name__ == "__main__":
    topic = "Machine Learning Basics"
    description = "An introduction to fundamental concepts in machine learning"
    
    asyncio.run(generate_presentation(topic, description))