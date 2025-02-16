import pymupdf
import json
import os
from PIL import Image
import io
import hashlib
from pathlib import Path
import base64
import openai
from dotenv import load_dotenv
import asyncio
from typing import List, Dict
import aiofiles
from openai import AsyncOpenAI
import glob
# from iris import load_docs

# Load environment variables
load_dotenv()

async def get_image_description(image_path, page_text):
    """
    Get image description using OpenAI's Vision API asynchronously.
    """
    client = AsyncOpenAI()
    
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"What's in this image? Provide a brief, clear description. Provided is the accompanying text on the same page as the image that can be used as context for the image. Provide descriptive, quantitative descriptions about the image if possible (if it is a graph or diagram). {page_text}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
    except Exception as e:
        return "No description available"

async def process_single_image(img_data, pdf_document, page_num, output_dir, page_text):
    """
    Process a single image asynchronously
    """
    xref, img_index, total_images = img_data
    
    base_image = pdf_document.extract_image(xref)
    image_bytes = base_image["image"]
    
    image_hash = hashlib.md5(image_bytes).hexdigest()
    image_ext = base_image["ext"]
    filename = f"image_{image_hash}.{image_ext}"
    filepath = output_dir / filename
    
    async with aiofiles.open(filepath, "wb") as image_file:
        await image_file.write(image_bytes)
    
    with Image.open(io.BytesIO(image_bytes)) as img:
        width, height = img.size
    
    try:
        description = await get_image_description(filepath, page_text)
    except Exception as e:
        description = f"Image from page {page_num + 1}"
    
    return {
        "filepath": str(filepath),
        "page_number": page_num + 1,
        "width": width,
        "height": height,
        "description": description
    }

async def process_single_page(page_data: tuple) -> List[Dict]:
    """
    Process a single page of the PDF and extract its images asynchronously
    """
    pdf_document, page_num, output_dir = page_data
    page_metadata = []
    
    page = pdf_document[page_num]
    image_list = page.get_images()
    
    tasks = []
    for img_index, img in enumerate(image_list):
        img_data = (img[0], img_index, len(image_list))
        page_text = page.get_text("text")
        task = process_single_image(img_data, pdf_document, page_num, output_dir, page_text)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    page_metadata.extend(results)
    
    return page_metadata

async def extract_images_from_pdf(pdf_path, output_base_dir):
    """
    Extract images from a single PDF file
    """
    pdf_name = Path(pdf_path).stem
    output_dir = output_base_dir / pdf_name
    output_dir = os.path.join("pitcher/public", output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    pdf_document = pymupdf.open(pdf_path)
    print(f"Processing: {pdf_name}")
    
    page_data = [(pdf_document, page_num, output_dir) for page_num in range(len(pdf_document))]
    
    tasks = [process_single_page(data) for data in page_data]
    results = await asyncio.gather(*tasks)
    
    all_metadata = [item for sublist in results for item in sublist]
    
    json_path = output_dir / f"{pdf_name}_metadata.json"
    async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(all_metadata, indent=2))
    
    pdf_document.close()
    return all_metadata

async def process_directory(input_dir: str = "text_data", output_dir: str = "img"):
    """
    Process all PDF files in the specified directory
    """
    print("it reaches here")
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    json_path = Path("extracted_images")
    
    pdf_files = list(input_path.glob("**/*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    tasks = [extract_images_from_pdf(pdf_file, output_path) for pdf_file in pdf_files]
    all_results = await asyncio.gather(*tasks)
    combined_metadata = all_results[0]
    # combined_metadata = {
    #     str(pdf_files[i]): metadata 
    #     for i, metadata in enumerate(all_results)
    # }
    
    combined_json_path = json_path / "combined_metadata.json"
    async with aiofiles.open(combined_json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(combined_metadata, indent=2))
    
    total_images = sum(len(metadata) for metadata in all_results)
    print(f"Completed: {len(pdf_files)} PDFs, {total_images} images extracted")
    # load_docs(combined_json_path, "image_data")

async def main():
    try:
        await process_directory()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 