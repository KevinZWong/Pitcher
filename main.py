import os
import asyncio
from extraction import TextChunker
from summarizer import ChunkSummarizer


async def main():
    # Example usage
    directory = "data/session_20250215_005424_a_website_that_takes_in_user's_journal_entries_and"

    # Initialize the TextChunkers and Summarizer
    chunker = TextChunker(model="gpt-4o-mini", max_tokens=10000)
    summarizer = ChunkSummarizer()

    # Process the directory and get file information
    file_info = chunker.process_directory(directory)

    total_tokens = 0
    total_size = 0

    print("Found files:")
    for file_path, info in file_info.items():
        print(f"- {file_path}:")
        print(f"    Size: {info['size']} bytes")
        print(f"    Tokens: {info['tokens']}")
        
        if 'chunks' in info:
            print(f"    Split into {len(info['chunks'])} chunks:")
            for i, chunk in enumerate(info['chunks'], 1):
                print(f"      Chunk {i}: {chunk['tokens']:,} tokens - Saved to: {chunk['path']}")
        
        if info['tokens'] > 0:  # Only count valid token counts
            total_tokens += info['tokens']
        if info['size'] > 0:    # Only count valid file sizes
            total_size += info['size']

    print("\nSummary:")
    print(f"Total Tokens: {total_tokens:,}")
    print(f"Total Size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    chunks_dir = os.path.join(os.path.dirname(os.path.dirname(directory)), 'chunks')
    print(f"Chunks saved to: {chunks_dir}")

    # Process the chunks and create summary
    print("\nGenerating summary from chunks...")
    output_file = os.path.join(os.path.dirname(directory), "summary.txt")
    await summarizer.process_chunks_directory(chunks_dir, output_file)
    print(f"Summary has been saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())





