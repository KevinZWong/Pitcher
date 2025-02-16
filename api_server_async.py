from flask import Flask, request, send_file
from flask_cors import CORS
import asyncio
import os
import shutil
import tempfile
import subprocess
import traceback
from git import Repo
import requests
from pathlib import Path
from temprunner import generate_slides, process_code_directory
from temprunner import extract_text_from_pdf as extract_text_code_main
from drive_extract import DriveDownloader
from extract_links import download_from_github
from extract_text_code import process_code, process_text
from imgextract import process_directory
from marp_slides import create_presentation_graph
import time
from graphs.process import image_gen

app = Flask(__name__)
CORS(app)

async def process_drive_data(drive_url):
    downloader = DriveDownloader()
    try:
        downloader.download_folder(drive_url, 'text_data',)
        await process_text()
        await process_directory()
        return True
    except Exception as e:
        print(f"Error in drive processing: {e}")
        return False

async def process_github_data(github_url):
    try:
        download_from_github(github_url)
        await process_code()
        shutil.rmtree('code_data', ignore_errors=True)
        return True
    except Exception as e:
        print(f"Error in github processing: {e}")
        return False

def create_slides(prompt):
    try:
        topic = "Sales pitch"
        
        # Read summaries
        text_summary = ""
        code_summary = ""
        with open("extract/summary/text_summary.txt", "r") as file:
            text_summary = file.read()
        with open("extract/summary/code_summary.txt", "r") as file:
            code_summary = file.read()
        
        # Create and process graph
        graph = create_presentation_graph()
        result = graph.invoke({
            "topic": topic,
            "requirements": prompt,
            "text_context": text_summary,
            "code_context": code_summary
        })

        # Create markdown and convert to HTML
        with open("presentation.md", "w") as file:
            file.write(result['slides']['marp_markdown'])
        
        output_html = "presentation.html"
        subprocess.run(["marp", "presentation.md", "-o", output_html], check=True)
        return True
    except Exception as e:
        import traceback
        print(f"Error in slide creation: {e}")
        print(traceback.format_exc())
        return False

@app.route('/api/projects', methods=['POST'])
async def process_project():
    try:
        data = request.json
        prompt = data.get('prompt')
        github_url = data.get('githubUrl')
        drive_url = data.get('driveUrl')

        if not any([prompt, github_url, drive_url]):
            return {'error': 'No content to process'}, 400

        # Run all processes concurrently
        tasks = []
        if drive_url:
            tasks.append(process_drive_data(drive_url))
        if github_url:
            tasks.append(process_github_data(github_url))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        image_gen()
        if prompt:
            create_slides(prompt)
        # # Check if any task failed
        # if any(isinstance(result, Exception) for result in results):
        #     return {'error': 'One or more processes failed'}, 500
        return {'message': 'All processes completed successfully',
                'filename': 'presentation.html'}, 200

    except Exception as e:
        print("An error occurred:", e)
        return {'error': str(e)}, 500

if __name__ == '__main__':
    print("Starting server...")
    # Use an ASGI server like hypercorn to run async Flask
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = ["localhost:5000"]
    asyncio.run(serve(app, config))