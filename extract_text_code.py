import os
import asyncio
from pathlib import Path
from extract.summarizer import TextProcessor
from extract.chunker import TextChunker
from dotenv import load_dotenv


async def is_directory_empty(directory: str) -> bool:
    """Check if a directory is empty."""
    path = Path(directory)
    if not path.exists():
        path.mkdir(parents=True)
        return True
    return not any(path.iterdir())


async def process_and_feature_extract_files(chunks_dir, text_data_dir, summary_dir, feature_extraction_prompt):
    chunker = TextChunker(model="gpt-4", max_tokens=10000)
    # cleanup chunks directory
    if chunks_dir.exists():
        for chunk_file in chunks_dir.glob("*_chunk_*.txt"):
            chunk_file.unlink()

    # Process the data directory and get file information
    print("\nProcessing files into 10k token chunks...")
    file_info = chunker.process_directory(str(text_data_dir))

    total_tokens = 0
    total_size = 0
    total_chunks = 0

    for file_path, info in file_info.items():
        file_type = info.get('type', 'unknown')
        
        if 'chunks' in info:
            num_chunks = len(info['chunks'])
            total_chunks += num_chunks
        if info['tokens'] > 0:  # Only count valid token counts
            total_tokens += info['tokens']
        if info['size'] > 0:    # Only count valid file sizes
            total_size += info['size']

    print("\nSummary:")
    print(f"Total Files: {len(file_info)}")
    print(f"Total Chunks: {total_chunks}")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print(f"Average Tokens per Chunk: {total_tokens/total_chunks:,.0f}" if total_chunks > 0 else "No chunks created")
    print(f"Chunks saved to: {chunks_dir}")

    output_file = summary_dir / "text_summary.txt"
    summarizer = TextProcessor(mode="extract")
    await summarizer.process_directory(str(chunks_dir), str(output_file))
    print(f"Summary has been saved to: {output_file}")


async def process_and_summarize_files(code_data_dir, summary_dir, summary_prompt):
    summarizer = TextProcessor(mode="summarize")
    output_file = summary_dir / "code_summary.txt"
    await summarizer.process_directory(str(code_data_dir), str(output_file))
    print(f"Summary has been saved to: {output_file}")


async def process_text_and_code():
    """
    Main processing function for text and code analysis
    """
    # Set up directories
    base_dir = Path("text_extract")
    text_data_dir = Path("text_data")
    code_data_dir = Path("code_data")
    chunks_dir = base_dir / "chunks"
    summary_dir = base_dir / "summary"

    # Create directories if they don't exist
    for directory in [chunks_dir, summary_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    feature_extraction_prompt = """You are an expert in extracting key information from text. Convert the input text into a series of short, clear statements.
        Instructions:
        - Extract key facts, insights, statistics, and details
        - Write each piece of information as a single, clear statement
        - Use bullet points for each statement
        - Be concise and direct
        - Include only factual information from the text
        - Do not add any headers, introductions, or conclusions
        - Do not add any meta-commentary or labels
        - Do not group or categorize the information
        - Do not repeat information
        """

    summary_prompt = """You are an expert in summarizing and finding the purpose of code. Convert the input code into a concise summary.
        Instructions:
        - Write a summary of the input code
        - Be concise and direct
        - Include only factual information from the code
        - Do not add any headers, introductions, or conclusions
        - Do not add any meta-commentary or labels
        """

    await process_and_feature_extract_files(chunks_dir, text_data_dir, summary_dir, feature_extraction_prompt)    
    await process_and_summarize_files(code_data_dir, summary_dir, summary_prompt)
    
    # load_docs("extract/summary", "current")


async def main():
    load_dotenv()
    print("Starting processing...")
    await process_text_and_code()


if __name__ == "__main__":
    asyncio.run(main())
