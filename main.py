import os
import asyncio
from pathlib import Path
from extraction import TextChunker
from summarizer import ChunkSummarizer
from synethic_data import StartupDataGenerator
from dotenv import load_dotenv
from iris import load_docs

async def is_directory_empty(directory: str) -> bool:
    """Check if a directory is empty."""
    path = Path(directory)
    if not path.exists():
        path.mkdir(parents=True)
        return True
    return not any(path.iterdir())

async def main():


    load_dotenv()
    
    # Set up directories
    data_dir = Path("data")
    chunks_dir = Path("chunks")
    summary_dir = Path("Summary")

    # Create directories if they don't exist
    for directory in [data_dir, chunks_dir, summary_dir]:
        directory.mkdir(exist_ok=True)

    # Check if data directory is empty
    if await is_directory_empty(data_dir):
        print("Data directory is empty. Generating startup analysis...")
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate API key
        if not api_key:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")
        
        # Initialize the StartupDataGenerator
        generator = StartupDataGenerator(api_key=api_key)
        
        idea = "A website that takes in user's journal entries and gives AI summaries for each, allows for sentinent analysis and mood tracking, and gives song recommendation."
        await generator.generate_and_save_startup_data(idea)
        print("Startup analysis generation complete.")

    # Initialize the TextChunker with exactly 20k tokens per chunk
    chunker = TextChunker(model="gpt-4o-mini", max_tokens=20000)
    summarizer = ChunkSummarizer()

    # Clean up old chunks if they exist
    if chunks_dir.exists():
        for chunk_file in chunks_dir.glob("*_chunk_*.txt"):
            chunk_file.unlink()

    # Process the data directory and get file information
    print("\nProcessing files into 20k token chunks...")
    file_info = chunker.process_directory(str(data_dir))

    total_tokens = 0
    total_size = 0
    total_chunks = 0

    print("\nProcessed files:")
    for file_path, info in file_info.items():
        file_type = info.get('type', 'unknown')
        print(f"\n- {file_path} ({file_type}):")
        print(f"    Size: {info['size']:,} bytes")
        print(f"    Tokens: {info['tokens']:,}")
        
        if 'chunks' in info:
            num_chunks = len(info['chunks'])
            total_chunks += num_chunks
            print(f"    Split into {num_chunks} chunks ({20000:,} tokens each):")
            for i, chunk in enumerate(info['chunks'], 1):
                print(f"      Chunk {i}: {chunk['tokens']:,} tokens - {chunk['path']}")
        
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

    # Process the chunks and create summary
    print("\nGenerating summary from chunks...")
    output_file = summary_dir / "summary.txt"
    await summarizer.process_chunks_directory(str(chunks_dir), str(output_file))
    print(f"Summary has been saved to: {output_file}")



if __name__ == "__main__":
    asyncio.run(main())





