import time
from typing import List, Optional, Union, Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, START, END
import asyncio
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
# from image_gen import create_mermaid_charts
from imagerag import search_q


load_dotenv()

'''
Approach: 
-> Have an LLM create a layout of the entire deck in bullet points and place placeholder images for that
-> [Optional] create a slide using aynchronous approach that you did previously
-> create the images using some programmatic approach, making an LLM spit out code that makes that image 
-> run the code and save these images in a folder/(pre-dertemined path by the first LLM call)
-> render the pdf
'''

class SlideModel(BaseModel):
    marp_markdown: str
    image_placeholder_filenames: List[str]
    image_placeholder_desc: List[str]

class ImageRelevance(BaseModel):
    score: float

def create_presentation_outline(context: dict) -> dict:
    """
    First node in the presentation pipeline that generates a MARP markdown outline
    with image placeholders and descriptions.
    
    Args:
        context (dict): Contains presentation topic, requirements, and any other context
        
    Returns:
        dict: Updated context with generated markdown and image descriptions
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
    You are an expert MARP presentation designer who creates clear, engaging slide decks using MARP.
    Your task is to generate a presentation in MARP format based on the provided topic and context.

    The marp_markdown MUST start with this exact MARP frontmatter:
    ---
    marp: true
    theme: default
    paginate: true
    size: 16:9
    ---
    
    Follow these key requirements:
    1. Include Marp headers (marp:true etc)
    2. Create a logical flow from introduction to conclusion
    3. Include image placeholders using standard markdown image syntax: ![alt_text](path)
    4. For each image placeholder:
    - Use a folder for the paths named "imgs"
    - Use a unique identifier like {{"imgs/img_1.png"}}, {{"imgs/img_2.png"}} etc. as the path (the folder is common however)
    - Provide a detailed description of what the image should contain in HTML comments below the image tag, this must be ~ 150 words
    <!-- Image description: A detailed explanation of what should be generated -->
    5. Every Slide should have one or more images, especially charts, schematics and diagrams
    6.  What you create must be in MARP syntax and should be able to be converted to slide decks using marp cli 

    Keep in mind:
    - Aim for visual slides with minimal text
    - Use clear headers and bullet points
    - Include diagrams/visualizations where they add value
    - Maintain consistent styling throughout
    - Create ~1 image per 2-3 slides on average

    The output should be valid MARP that could be rendered directly (except for placeholder images).
"""

    structured_llm = llm.with_structured_output(SlideModel)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": 
         f"Create a presentation about: {context['topic']} using this context: {context['context']}\n\n"
                                   f"Additional requirements: {context.get('requirements', '')}"}
    ]
    print("Sending LLM layout call")
    response = structured_llm.invoke(messages)
    context.update({
        "slides": response.model_dump(),
        "generated_at": time.time()
    })
    print(f"Received layout (Time Taken {time.time() - start_time})")
    return context


def rag_search_image(context: dict) -> dict:
    for i in range(len(context['slides']['image_placeholder_desc'])):

        desc = context['slides']['image_placeholder_desc'][i]
        ret = search_q(query= desc, k=1)
        # Prepare the prompt for the LLM call
        prompt = f"Is the image retrieved from the RAG search relevant to the description: {desc}?"
        
        # Initialize the LLM with structured output
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
        structured_llm = llm.with_structured_output(ImageRelevance)
        
        # Make the LLM calcdl
        response = structured_llm.invoke(prompt)

        # Check if the response indicates relevance
        if response.score >= 0.0:
            context['slides']['image_placeholder_filenames'][i] = ret['filepath']
            filename = context['slides']['image_placeholder_filenames'][i]
            print(f"Image {filename} is relevant to the description: {desc}")
        else:
            print(f"Image {filename} is not relevant to the description: {desc}\n"
                  f"The score was {response['score']}")
        return context

# Example of creating the graph
def create_presentation_graph() -> Graph:
    workflow = Graph()
    
    workflow.add_node("create_outline", create_presentation_outline)
    # workflow.add_node("create_mermaid_charts", create_mermaid_charts)
    workflow.add_node("rag_image", rag_search_image)
    # Add edges
    # workflow.add_edge("create_outline", "create_mermaid_charts")
    workflow.set_entry_point("create_outline")

    workflow.add_edge("create_outline", 'rag_image')
    workflow.add_edge("rag_image", END)
    
    return workflow.compile()


if __name__ == "__main__":
    topic = "Sales pitch: MoodMuse"
    with open("summary.txt", "r") as file:
        summary_content = file.read()
    num_slides = 10
    start_time = time.time()
    graph = create_presentation_graph()
    result = graph.invoke({
        "topic": topic,
        "requirements": "Include visuals",
        "context": summary_content
    })
    with open("presentation.md", "w") as file:
        file.write(result['slides']['marp_markdown'])
    end_time = time.time()

    for filename, desc in zip(result['slides']['image_placeholder_filenames'], result['slides']['image_placeholder_desc']):
        with open("placeholder_images.txt", "a") as file:
            file.write(f"{filename}: {desc}\n")
    
    print(result)
    print("time taken:", end_time - start_time)

