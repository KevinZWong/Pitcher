from openai import OpenAI
import os
from dotenv import load_dotenv
from pget import extract_image_urls_and_descriptions
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def get_pitch():
    with open("../presentation.md", 'r') as f:
            markdown_content = f.read()
    desc=extract_image_urls_and_descriptions("../presentation.md", "../extracted_images/combined_metadata.json")
    messages = [
        {
            "role": "system",
            "content": 
                f"""You are an expert at giving presentations. I am going to give you a presentation and your job is to generate a speech that can go along
                with it. Make sure you make it funny and relatable. Genrate the content by seperating it by slides. 
                Do not add too much content and make sure you seperate the slides clearly  by ========================
                
                            """
    }  
    ]

    client=OpenAI()
    formatted_user_query = f"""
                Here is the presentation: {markdown_content}
                Here are the descriptions of all the images in the presentation: {desc}

        
    """
    messages.append(
            {
                'role': 'user',
                'content': formatted_user_query
            })
    routput = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    out =  routput.choices[0].message.content
    print(out)
    return out

get_pitch()