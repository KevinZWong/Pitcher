from flask import Flask, request, send_file
from flask_cors import CORS
import os
import shutil
import tempfile
import subprocess
from git import Repo
import requests
from pathlib import Path
#from runner import generate_slides, process_code_directory, extract_text_from_pdf as extract_text_code_main
from temprunner import generate_slides, process_code_directory
from temprunner import extract_text_from_pdf as extract_text_code_main
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def download_drive_file(drive_url):
    # This is a placeholder - you'll need to implement proper Google Drive download
    # Consider using google-api-python-client or a similar library
    response = requests.get(drive_url)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

@app.route('/api/projects', methods=['POST'])
def process_project():
    try:
        data = request.json
        prompt = data.get('prompt')
        github_url = data.get('githubUrl')
        drive_url = data.get('driveUrl')
        
        # Create a temporary working directory
        with tempfile.TemporaryDirectory() as temp_dir:
            content = []
            
            # Process Google Drive PDF if provided
            if drive_url:
                pdf_path = download_drive_file(drive_url)
                content.extend(extract_text_code_main(pdf_path))
                print("drive_url from the backend!", drive_url)
                os.unlink(pdf_path)  # Clean up the PDF file
            
            # Process GitHub repository if provided
            if github_url:
                repo_dir = os.path.join(temp_dir, 'repo')
                print("github_url from the backend!", github_url)
                Repo.clone_from(github_url, repo_dir)
                
                # Decide which processor to use based on your criteria
                # Here we're using describe.py for code processing
                content.extend(process_code_directory(repo_dir))
                
                # Clean up happens automatically when tempfile directory is closed
            
            # Generate slides using marp
            if content:
                # Combine all content and pass to prompt
                combined_content = "\n".join(content)
                print("prompt from the backend!", prompt)
                slides_html = generate_slides(prompt, combined_content)
                # Save the HTML file
                output_path = os.path.join('pitcher', 'public', 'slides.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(slides_html)
                
                return {'filename': 'slides.html'+' '.join(content)}, 200

            return {'error': 'No content to process'}, 400
            
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    print("Starting server...")
    app.run(debug=True, port=5000) 