import time
from typing import List, Optional, Union, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, START, END
from langchain_groq import ChatGroq
import asyncio
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

'''
Approach: 
-> Have an LLM create a layout of each slide
-> search for relevant images using some image search api (works concurrently) 
-> 
'''


start_time = time.time()

load_dotenv()

# Data structures
@dataclass
class Slide:
    title: str
    content: str
    layout: str

@dataclass
class PresentationState:
    topic: str
    context: str
    num_slides: int
    slides: List[Slide]
    current_state: str  # "planning", "generating", "combining"

# Nested models for layout components
class Position(BaseModel):
    x: str
    y: str

class Size(BaseModel):
    width: str
    height: str

class TextElement(BaseModel):
    content: str
    position: Literal["left", "right", "center", "top", "bottom"]
    char_limit: int
    style: Literal["heading", "body", "bullet"]

class VisualElement(BaseModel):
    type: Literal["chart", "diagram", "icon", "photo"]
    position: Position
    size: Size
    description: str
    visualization_type: Literal["pie", "bar", "line", "mermaid", "image"]

class Animation(BaseModel):
    element: str
    type: Literal["fade", "slide", "zoom"]
    trigger: Literal["auto", "click"]
    duration: Literal["fast", "medium", "slow"]

class Background(BaseModel):
    color: str
    gradient: bool

class Layout(BaseModel):
    text_elements: List[TextElement]
    visual_elements: List[VisualElement]
    animations: List[Animation]
    background: Background

class GlobalStyle(BaseModel):
    color_scheme: List[str]
    font_family: str
    transition: str

class SlidePlan(BaseModel):
    title: str = Field(..., description="The title of the slide")
    layout: Layout = Field(..., description="The layout of the slide")

class PresentationPlan(BaseModel):
    slides: List[SlidePlan] = Field(..., description="List of slides in the presentation")
    global_style: GlobalStyle

# Agent definitions
class PresentationPlanner:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def plan_presentation(self, state: PresentationState) -> PresentationState:
        prompt = f"""
        Create a detailed slide layout plan for a presentation on {state.topic} using {state.num_slides} slides. Extract ALL KEY information from the given context.

        Context: {state.context} 

        For each slide, provide:
        1. Slide title
        2. Detailed Layout Plan including:
            - Text content locations with character limits
            - Image/visual specifications:
                - Type (chart/diagram/icon/photo)
                - Position (x,y coordinates or grid position)
                - Size (width/height in %)
                - Description of what the image should show
            - Animations/transitions (if any)
            - Color scheme suggestions

        Format your response as JSON with the following structure:
        {{
            "slides": [
                {{
                    "title": "string",
                    "layout": {{
                        "text_elements": [
                            {{
                                "content": "string",
                                "position": "left|right|center|top|bottom",
                                "char_limit": integer,
                                "style": "heading|body|bullet"
                            }}
                        ],
                        "visual_elements": [
                            {{
                                "type": "chart|diagram|icon|photo",
                                "position": {{
                                    "x": "string",
                                    "y": "string"
                                }},
                                "size": {{
                                    "width": "string",
                                    "height": "string"
                                }},
                                "description": "Detailed description of what this visual should show",
                                "visualization_type": "pie|bar|line|mermaid|image"
                            }}
                        ],
                        "animations": [
                            {{
                                "element": "reference to text/visual element",
                                "type": "fade|slide|zoom",
                                "trigger": "auto|click",
                                "duration": "fast|medium|slow"
                            }}
                        ],
                        "background": {{
                            "color": "string",
                            "gradient": boolean
                        }}
                    }}
                }}
            ],
            "global_style": {{
                "color_scheme": ["primary", "secondary", "accent"],
                "font_family": "string",
                "transition": "string"
            }}
        }}

        Instructions:
        1. Minimize text - keep it concise and impactful
        2. Prioritize visuals - use charts, diagrams, and images strategically
        3. Ensure all position values are in percentages for responsive design
        4. Provide specific visualization types for charts/diagrams
        5. Include detailed descriptions for each visual element
        6. Maintain consistent style across slides

        Do not respond with anything apart from the JSON.
        """
        
        # Use the LLM to generate structured output
        response = await self.llm.ainvoke(
            [SystemMessage(content="You are a presentation planning expert."),
             HumanMessage(content=prompt)]
        )
        
        try:
            # Parse the response into the PresentationPlan model
            
            response.content = response.content.replace("```json", "").replace("```", "") #weeding out response bs
            with open("presentation_plan.json", "w") as file:
                file.write(response.content)
            plan = PresentationPlan.model_validate_json(response.content)
            state.slides = [Slide(**slide.dict(), content="") for slide in plan.slides]
            print(state.slides[0])
            state.current_state = "generating"
        except Exception as e:
            raise ValueError(f"Invalid response from LLM: {e}")
            
        return state

class SlideGenerator:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def generate_slide(self, slide: Slide, topic: str) -> Slide:
        prompt = f"""
        Generate content for a presentation slide about {slide.title} using the entire breadth of the screen.
        Slide title: {slide.title}
        Layout: {slide.layout}

        Return only the content code without any explanation without ```html, just the code as text.
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
                    hash: true,

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
        slide_ind = 0
        for slide in slides:
            # if slide.content_type == "mermaid":
            #     content = f'<div class="mermaid">{slide.content}</div>'
            # elif slide.content_type == "d3":
            #     content = f'<div id="d3-{slide_ind}" class="d3-container"></div><script>{slide.content}</script>'
            # else:
            content = slide.content    
            slide_sections.append(f'<section><h2>{slide.title}</h2>{content}</section>')
            slide_ind+=1
        
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
async def generate_presentation(topic: str, context: str, num_slides: Optional[int] = None):
    if num_slides is None:
        # Ask for number of slides using Groq
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
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
        context=context,
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
    topic = "Sales pitch: MoodMuse"
    with open("summary.txt", "r") as file:
        summary_content = file.read()
    num_slides = 10
    start_time = time.time()
    asyncio.run(generate_presentation(topic, context = summary_content, num_slides=num_slides))
    end_time = time.time()
    print("time taken:", end_time - start_time)