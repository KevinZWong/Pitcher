import traceback
from flask import Flask, request, send_file
from flask_cors import CORS
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
from extract_text_code import process_code, process_text, process_code_wrapper, process_text_wrapper
from imgextract import process_directory
from marp_slides import create_presentation_graph
import time
from graphs.process import image_gen

app = Flask(__name__)
CORS(app)

def process_drive_data(drive_url):
    downloader = DriveDownloader()
    try:
        downloader.download_folder(drive_url, 'text_data')
        # Convert async functions to sync
        process_text_wrapper()
        process_directory()
        return True
    except Exception as e:
        print(f"Error in drive processing: {e}")
        return False

def process_github_data(github_url):
    try:
        download_from_github(github_url)
        # Convert async process_code to sync
        process_code_wrapper()
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
        
        output_html = "pitcher/public/presentation.html"
        subprocess.run(["marp", "presentation.md", "-o", output_html], check=True)
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error in slide creation: {e}")
        print(traceback.format_exc())
        return False

@app.route('/api/projects', methods=['POST'])
def process_project():
    try:
        start_time = time.time()
        data = request.json
        prompt = data.get('prompt')
        github_url = data.get('githubUrl')
        drive_url = data.get('driveUrl')

        if not any([prompt, github_url, drive_url]):
            return {'error': 'No content to process'}, 400

        # Process sequentially instead of concurrently
        if drive_url:
            process_drive_data(drive_url)
        if github_url:
            process_github_data(github_url)
        
        # Generate images
        image_gen()
        
        if prompt:
            create_slides(prompt)
        time.sleep(2)
        print("Time_take: ", time.time() - start_time)
        return {'message': 'All processes completed successfully',
                'filename': 'presentation.html'}, 200

    except Exception as e:
        
        print("An error occurred:", e)
        print(traceback.format_exc())
        return {'error': str(e)}, 500

@app.route('/api/presentation-status', methods=['GET'])
def find_status():
    try:
        with open("status.txt", "r") as file:
            content = file.read()
            if "Move" in content:
                with open('status.txt', 'w') as f:
                    f.write("not ready")
                return {'status': 'Yes'}, 200
            else:
                return {'status': 'Wait'}, 200
    except FileNotFoundError:
        return {'error': 'status.txt file not found'}, 404


if __name__ == '__main__':
    print("Starting server...")
    # Use regular Flask development server instead of hypercorn
    app.run(host='localhost', port=5000, debug=True)