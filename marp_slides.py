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
# from imagerag import search_q


load_dotenv()

#inital prompts
#  3. Include image placeholders using standard markdown image syntax: ![alt_text](path)
#     4. For each image placeholder:
#     - Use a folder for the paths named "imgs"
#     - Use a unique identifier like {{"imgs/img_1.png"}}, {{"imgs/img_2.png"}} etc. as the path (the folder is common however)
#     - Provide a detailed description of what the image should contain in HTML comments below the image tag, this must be ~ 150 words
#     <!-- Image description: A detailed explanation of what should be generated -->


class SlideModel(BaseModel):
    marp_markdown: str
    # image_placeholder_filenames: List[str]
    # image_placeholder_desc: List[str]

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
    3. Every Slide MUST have one or more elements such as images, charts, schematics and diagrams
    4. What you create must be in MARP syntax and should be able to be converted to slide decks using marp cli 
    
    Keep in mind:
    - Keep minimal text, leave space for visuals
    - do not include any visuals
    - Use clear headers and bullet points
    - Include diagrams/visualizations where they add value
    - Maintain consistent styling throughout
    - Make sure to leave room for images to be added

    The output should be valid MARP that could be rendered directly.
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
    print(f"Received textual layout (Time Taken {time.time() - start_time})")
    return context


def edit_presentation_outline(context: dict) -> dict:
    """
    Second node in the presentation pipeline that generates a MARP markdown outline
    with image placeholders and descriptions.
    
    Args:
        context (dict): Contains presentation topic, requirements, and image descriptions
        
    Returns:
        dict: Updated context with generated markdown and image descriptions
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
   You are an expert MARP presentation editor who creates clear, engaging slide decks using MARP.
Your task is to edit the given layout by precisely matching provided image descriptions with relevant slide content.

The marp_markdown MUST start with this exact MARP frontmatter:
---
marp: true
theme: default
paginate: true
size: 16:9
---

Your PRIMARY responsibility is to:
    SELECT THE MOST RELEVANT IMAGE for each slide—choose the best possible match that enhances understanding and engagement.
    It is important to have at least one image per slide while. Do not force an image if it does not fit. If no good match exists, DO NOT include an completely unrelated image.
    Integrate images naturally:
    Match each provided image description to the most relevant slide content.
    Insert the corresponding image filename in that section.
    Modify the slide text to explicitly connect with the image’s content.
    Ensure GOOD SPACING between text and images for easy comprehension.
    Maintain the original aspect ratio of all images to avoid distortion.
    Confirm that images are of appropriate resolution and clearly visible in the slide format.
    Include image dimensions as comments to validate size accuracy.
Strict Requirements:
    Keep all original MARP headers and formatting (e.g., marp:true).
    Ensure text remains minimal while still directly referencing the image’s content.
    NEVER invent or suggest new images—only use the explicitly provided filenames.
    Do NOT force an image if it doesn’t fit—only include those that truly enhance the content.
The output must be valid MARP markdown that could be rendered directly.
"""

    structured_llm = llm.with_structured_output(SlideModel)
    

    # Load the combined metadata from the JSON file
    combined_metadata_path = os.path.join("extracted_images", "combined_metadata.json")
    image_metadata = None
    with open(combined_metadata_path, "r") as file:
        image_metadata = json.load(file)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": 
         f"Edit the presentation that has the following marp layout {context['slides']['marp_markdown']} to include relevant images that has the following images: {image_metadata}\n\n"}
    ]
    print("Sending LLM layout EDIT call ")

    call2_start_time = time.time() #for keeping time 

    response = structured_llm.invoke(messages)
    context.update({
        "slides": response.model_dump(),
        "generated_at": time.time()
    })
    print(f"Received edited layout (Time Taken {time.time() - call2_start_time})")

    return context


def style_presentation_outline(context: dict) -> dict:
    """
    Third node in the presentation pipeline that generates a MARP markdown outline
    with image placeholders and descriptions.
    
    Args:
        context (dict): Contains presentation topic, requirements, and image descriptions
        
    Returns:
        dict: Updated context with generated markdown and image descriptions
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = f"""
You are creating a MARP presentation. Your primary focus is proper image scaling and styling.

Must start with:
---
marp: true
theme: default
paginate: true
size: 16:9
---

Image Rules:
1. EVERY image must include size directives - NO exceptions
2. Use these patterns:
   - Charts/graphs: ![w:800 h:400](path/to/image.png)
   - Flowcharts: ![w:900](path/to/image.png)
   - Side images: ![bg right:40% w:400](path/to/image.png)
3. Make each slide aesthetically pleasing and aligned
4. Make sure each image is the correct size and fits the slide


Keep in mind:
- Never exceed slide boundaries
- Maximum 2 images per slide
- Leave adequate whitespace around images
- Center single images
- Use bg right/left for text + image layouts

"""

    structured_llm = llm.with_structured_output(SlideModel)


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": 
         f"Style the presentation that has the following marp layout {context['slides']['marp_markdown']} to include relevant images that has the following images:\n\n"}
    ]
    print("Sending LLM layout STYLE call ")

    call3_start_time = time.time() #for keeping time 

    response = structured_llm.invoke(messages)
    context.update({
        "slides": response.model_dump(),
        "generated_at": time.time()
    })
    print(f"Received edited layout (Time Taken {time.time() - call3_start_time})")

    return context

# def rag_search_image(context: dict) -> dict:
#     for i in range(len(context['slides']['image_placeholder_desc'])):

#         desc = context['slides']['image_placeholder_desc'][i]
#         ret = search_q(query= desc, k=1)
#         # Prepare the prompt for the LLM call
#         prompt = f"Is the image retrieved from the RAG search relevant to the description: {desc}?"
        
#         # Initialize the LLM with structured output
#         llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
#         structured_llm = llm.with_structured_output(ImageRelevance)
        
#         # Make the LLM calcdl
#         response = structured_llm.invoke(prompt)

#         # Check if the response indicates relevance
#         if response.score >= 0.0:
#             context['slides']['image_placeholder_filenames'][i] = ret['filepath']
#             filename = context['slides']['image_placeholder_filenames'][i]
#             print(f"Image {filename} is relevant to the description: {desc}")
#         else:
#             print(f"Image {filename} is not relevant to the description: {desc}\n"
#                   f"The score was {response['score']}")
#         return context



# Example of creating the graph
def create_presentation_graph() -> Graph:
    workflow = Graph()
    
    workflow.add_node("create_outline", create_presentation_outline)
    workflow.add_node("edit_outline", edit_presentation_outline)
    workflow.add_node("style_outline", style_presentation_outline)

    # workflow.add_node("rag_image", rag_search_image)
    # workflow.add_edge("create_outline", "create_mermaid_charts")
    # Add edges
    workflow.add_edge("create_outline", 'edit_outline')
    workflow.add_edge("edit_outline", 'style_outline')
    workflow.add_edge("style_outline", END)
    
    workflow.set_entry_point("create_outline")
    return workflow.compile()


if __name__ == "__main__":
    topic = "Sales pitch: MoodMuse"

    #get the summary context
    with open("summary.txt", "r") as file:
        summary_content = file.read()
    num_slides = 10
    
    start_time = time.time()

    #create the grpah and start it
    graph = create_presentation_graph()
    result = graph.invoke({
        "topic": topic,
        "requirements": "Include visuals",
        "context": summary_content,
    })

    #make the mardown
    with open("presentation.md", "w") as file:
        file.write(result['slides']['marp_markdown'])
    end_time = time.time()

    #just for knwoing what the names and descritpionf ot he needed placeholder are (DEPRECATED NOW)
    # for filename, desc in zip(result['slides']['image_placeholder_filenames'], result['slides']['image_placeholder_desc']):
    #     with open("placeholder_images.txt", "a") as file:
    #         file.write(f"{filename}: {desc}\n")
    
    print(result)
    print("time taken:", end_time - start_time)

