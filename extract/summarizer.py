import os
import asyncio
from openai import AsyncOpenAI
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional, Literal
import tiktoken

# Load environment variables from .env file
load_dotenv()

class TextProcessor:
    def __init__(self, mode: Literal["extract", "summarize"] = "extract", api_key=None, max_tokens: int = 4000):
        """
        Initialize the TextProcessor.
        
        Args:
            mode (str): Processing mode - either "extract" for feature extraction or "summarize" for summarization
            api_key (str, optional): OpenAI API key. If not provided, will use environment variable
            max_tokens (int): Maximum tokens per chunk for feature extraction mode
        """
        self.mode = mode
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model("gpt-4")

        # Define prompts for different modes
        self.prompts = {
            "extract": """You are an expert in extracting key information from text. Convert the input text into a series of short, clear statements.

Instructions:
- Extract key facts, insights, statistics, and details
- Write each piece of information as a single, clear statement
- Use bullet points for each statement
- Be concise and direct
- Include only factual information from the text
- Do not add any headers, introductions, or conclusions
- Do not add any meta-commentary or labels
- Do not group or categorize the information
- Do not repeat information""",

            "summarize": """You are an expert summarizer. Create a clear, concise summary of the input text.

Instructions:
- Provide a comprehensive yet concise summary
- Maintain the key points and main ideas
- Keep the original meaning and context
- Use clear, professional language
- Focus on the most important information
- Organize the summary in a logical flow
- Include critical details and examples
- Aim for about 25% of the original length
- Make the summary standalone and understandable"""
        }

        self.system_prompt = self.prompts[mode]

    async def process_directory(self, chunks_dir: str, output_path: str) -> None:
        """
        Process all text-based files in the given directory and its subdirectories in parallel and save results to a file.
        
        Args:
            chunks_dir (str): Directory containing text files to process
            output_path (str): Path where the output text file will be saved
        """
        # Define common text file extensions
        text_extensions = {'.txt', '.md', '.rst', '.log', '.csv', '.json', '.xml', '.yml', '.yaml', '.ini', '.conf', '.py', '.js', '.html', '.css', '.tex'}
        
        # Get all text files in the directory and subdirectories
        chunks_path = Path(chunks_dir)
        text_files = []
        
        # Recursively search for text files
        for root, _, files in os.walk(chunks_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in text_extensions:
                    text_files.append(file_path)
        
        if not text_files:
            print(f"No text files found in {chunks_dir}")
            return

        # Prepare output file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        async def process_file(file_path: Path):
            try:
                # Read the file content
                chunk_text = file_path.read_text(encoding='utf-8', errors='ignore')
                
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": chunk_text}
                    ],
                    temperature=0.3,
                    max_tokens=16000
                )
                
                # Write result directly to file
                async with asyncio.Lock():
                    with open(output_path, 'a', encoding='utf-8') as f:
                        relative_path = file_path.relative_to(chunks_path)
                        f.write(f"\n=== {relative_path} ===\n\n")
                        f.write(response.choices[0].message.content)
                        f.write("\n\n")
                
                print(f"Processed {file_path.relative_to(chunks_path)}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

        # Process all files concurrently
        tasks = [process_file(file_path) for file_path in text_files]
        await asyncio.gather(*tasks)
        
        print(f"All results saved to {output_path}")
