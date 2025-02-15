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


# Load environment variables
load_dotenv()

def extract_images_from_pdf(pdf_path):
    # Create output directory if it doesn't exist
    output_dir = Path("extracted_images")
    output_dir.mkdir(exist_ok=True)
    
    # Dictionary to store image metadata
    image_metadata = []
    
    # Open PDF
    pdf_document = pymupdf.open(pdf_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            # Get image data
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            page_text = page.get_text("text")
            
            # Generate unique filename using hash of image data
            image_hash = hashlib.md5(image_bytes).hexdigest()
            image_ext = base_image["ext"]
            filename = f"image_{image_hash}.{image_ext}"
            filepath = output_dir / filename
            
            # Save image
            with open(filepath, "wb") as image_file:
                image_file.write(image_bytes)
            
            # Get image dimensions
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size
            
            # Get image description using OpenAI
            try:
                description = get_image_description(filepath, page_text)
            except Exception as e:
                description = f"Image from page {page_num + 1}"
                print(f"Error getting description: {e}")
            
            # Store metadata
            image_metadata.append({
                "filepath": str(filepath),
                "page_number": page_num + 1,
                "width": width,
                "height": height,
                "description": description
            })
    
    # Save metadata to JSON
    json_path = "image_metadata.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(image_metadata, f, indent=2)
    
    pdf_document.close()
    return image_metadata

def get_image_description(image_path, page_text):
    """
    Get image description using OpenAI's Vision API.
    Requires OPENAI_API_KEY in environment variables.
    """
    client = openai.OpenAI()
    
    try:
        with open(image_path, "rb") as image_file:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"What's in this image? Provide a brief, clear description. Provided is the accommanying text on the same page as the image that can be used as context for the image. {page_text}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode()}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "No description available"

def main():
    # Extract images from the generated pitch deck PDF
    pdf_path = "input.pdf"
    
    try:
        metadata = extract_images_from_pdf(pdf_path)
        print(f"Extracted {len(metadata)} images to 'extracted_images' folder")
        print("Image metadata saved to 'image_metadata.json'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 