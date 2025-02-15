import os
import asyncio
from openai import AsyncOpenAI
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()

class ChunkSummarizer:
    def __init__(self, api_key=None):
        # Use environment variable if no API key provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = AsyncOpenAI(api_key=self.api_key)

        self.system_prompt = """You are an expert in extracting key information from text. Convert the input text into a series of short, clear statements.

Instructions:
- Extract key facts, insights, statistics, and details
- Write each piece of information as a single, clear statement
- Use bullet points for each statement
- Be concise and direct
- Include only factual information from the text
- Do not add any headers, introductions, or conclusions
- Do not add any meta-commentary or labels
- Do not group or categorize the information
- Do not repeat information"""

    async def process_chunk(self, chunk_text: str) -> Optional[str]:
        """Process a single chunk of text using OpenAI API asynchronously"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": chunk_text}
                ],
                temperature=0.3,
                max_tokens=16000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")
            return None

    async def process_chunks(self, chunk_files: List[Path]) -> List[Dict[str, str]]:
        """Process multiple chunks concurrently"""
        tasks = []
        
        # Create tasks for all chunks
        for chunk_file in chunk_files:
            print(f"Creating task for {chunk_file.name}...")
            # Read chunk content
            with open(chunk_file, "r", encoding="utf-8") as infile:
                chunk_text = infile.read()
            
            # Create task for processing this chunk
            task = asyncio.create_task(self.process_chunk(chunk_text))
            tasks.append((chunk_file.name, task))
        
        # Wait for all tasks to complete
        summaries = []
        for filename, task in tasks:
            try:
                summary = await task
                if summary:
                    summaries.append({
                        "filename": filename,
                        "summary": summary
                    })
                else:
                    print(f"Failed to process {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
        
        return summaries

    async def process_chunks_directory(self, chunks_dir: str, output_file: str = "summary.txt"):
        """Process all chunks in a directory and save results to a file"""
        chunks_path = Path(chunks_dir)
        if not chunks_path.exists() or not chunks_path.is_dir():
            raise ValueError(f"Directory not found: {chunks_dir}")

        # Sort chunks to process them in order
        chunk_files = sorted([f for f in chunks_path.glob("*.txt")])
        
        # Process chunks concurrently
        summaries = await self.process_chunks(chunk_files)
        
        # Write results to file - no headers or sections, just pure information
        with open(output_file, "w", encoding="utf-8") as outfile:
            for summary_info in summaries:
                outfile.write(summary_info['summary'])
                outfile.write("\n\n")

async def main():
    # Initialize summarizer
    summarizer = ChunkSummarizer()

    # Process all chunks in the chunks directory
    chunks_dir = "chunks"
    output_file = "summary.txt"

    print(f"Starting to process chunks from {chunks_dir}")
    await summarizer.process_chunks_directory(chunks_dir, output_file)
    print(f"Summary has been saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 