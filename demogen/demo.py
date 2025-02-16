from scrapybara import Scrapybara
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
from datetime import datetime
import os
from dotenv import load_dotenv

def get_github_readme(repo_url):
    # Convert URL to raw content URL if needed
    if "github.com" in repo_url:
        raw_url = repo_url.replace("github.com", "raw.githubusercontent.com")
        if not raw_url.endswith("/main/README.md"):
            raw_url = raw_url.rstrip("/") + "/main/README.md"
    else:
        raw_url = repo_url

    response = requests.get(raw_url)
    return response.text

def extract_env_variables(readme_content):
    # Look for environment variables in common formats
    try:
        # Use relative path to the envs.txt file in the demogen directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, 'envs.txt')
        with open(env_path, 'r') as f:
            env_vars = f.read().strip()
        return env_vars
    except FileNotFoundError:
        print("Warning: envs.txt not found, continuing without environment variables")
        return ""


def generate_demo_steps(readme_content):
    load_dotenv()  # Load environment variables from .env file
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    context = []
    steps = []
    
    # Extract environment variables
    env_vars = extract_env_variables(readme_content)
    
    initial_prompt = f"""
    Given this GitHub repository README:
    
    README:
    {readme_content}
    
    Environment Variables found:
    {env_vars}
    
    Provide the FIRST step for installing and exploring this repository. Start with git clone <repo_url>` in bash.
    Return just a single command as a string, no other text. This should be executable by an AI agent.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": initial_prompt}]
    )
    
    first_step = eval(response.choices[0].message.content.strip())
    steps.append(first_step)
    
    outline_prompt = f"""
    Given this GitHub repository README:
    
    README:
    {readme_content}
    
    Environment Variables needed:
    {env_vars}
    
    Provide an outline of instructions for a user to install the repository, run the app, and explore the repository's functionality. 
    ALWAYS start with:
    1. `git clone <repo_url>` in bash
    2. cd into the repository folder
    3. If environment variables are needed, use {env_vars} to create a .env file with the required variables
    4. Run installation commands from the README
    5. Run the application.
    6. Explore the repository's functionality. By using the features list in the readme, write a set of clear, precise, simple, and short commands that tells the user where to click to explore and learn the most about their creation and the most important features/functionality.
       - this would look like "click /search", "enter DIN and click enter", "click /medication", "click profile", "change language", "click /medication", "click the audio icon", "click star icon"
    
    Create a list of interactive demo steps that would showcase the main functionality. read the terminal and use the url of the locally hosted website and navigate with that.

    Each step should be a clear instruction that can be executed by Scrapybara (a browser automation tool). Focus on visual, demonstrable actions.
    
    Return the steps as a list of python strings. Do not include any other text. All text should be a command for an AI agent to execute.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": outline_prompt}]
    )
    
    outline = eval(response.choices[0].message.content.strip())
    print(outline)
    
    # Execute first step and capture result
    response = client.act(
        model=Anthropic(),
        tools=[BashTool(instance), ComputerTool(instance), EditTool(instance)],
        system=UBUNTU_SYSTEM_PROMPT,
        prompt=first_step,
        on_step=lambda step: context.append(step.text)
    )
    
    # Iteratively get and execute next steps
    for _ in range(20):
        next_step_prompt = f"""
        Given this GitHub repository README:
        {readme_content}

        Environment Variables needed:
        {env_vars}

        The total steps should include:
        - Cloning the repo
        - Setting up environment variables in .env file
        - Installing dependencies
        - Running the app
        - Exploring the repository's functionality

        Previous steps and their results:
        {'\n'.join(f'Step {i+1}: {step}\nResult: {context[i]}' for i, step in enumerate(steps))}
        
        Based on these previous steps and their results, what should be the next step?
        If there are no more meaningful steps to take, respond with "DONE".
        Return just a single command as a string, no other text. This should be executable by an AI agent.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": next_step_prompt}]
        )
        
        next_step = response.choices[0].message.content.strip()
        if next_step == "DONE" or next_step == '"DONE"':
            break
            
        next_step = eval(next_step)
        steps.append(next_step)
        
        # Execute step and capture result
        response = client.act(
            model=Anthropic(),
            tools=[BashTool(instance), ComputerTool(instance), EditTool(instance)],
            system=UBUNTU_SYSTEM_PROMPT,
            prompt=next_step,
            on_step=lambda step: context.append(step.text)
        )
    
    return steps

# Load environment variables
load_dotenv()
client = Scrapybara(api_key=os.getenv('SCRAPYBARA_API_KEY'))

# Start the instance
instance = client.start_ubuntu(timeout_hours=1)
stream_url = instance.get_stream_url().stream_url
print(stream_url)
print('Initializing...')

# Import required tools
from scrapybara.tools import BashTool, ComputerTool, EditTool
from scrapybara.anthropic import Anthropic
from scrapybara.prompts import UBUNTU_SYSTEM_PROMPT

# Replace with the GitHub repo URL you want to demo
repo_url = "https://github.com/cheollie/medibase"
readme_content = get_github_readme(repo_url)
demo_steps = generate_demo_steps(readme_content)

print("\nCompleted Steps:")
for i, step in enumerate(demo_steps, 1):
    print(f"Step {i}: {step}")