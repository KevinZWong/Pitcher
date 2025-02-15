import os
from typing import List, Dict
import tiktoken
from pathlib import Path

class TextChunker:
    def __init__(self, model: str = "gpt-4", max_tokens: int = 20000):
        """
        Initialize the TextChunker with model and token settings.
        
        Args:
            model (str): The model to use for tokenization
            max_tokens (int): Maximum number of tokens per chunk
        """
        self.model = model
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)
    
    def save_chunks(self, chunks: List[str], original_file: str, output_dir: str = "chunks") -> List[str]:
        """
        Save chunks to separate files in the output directory.
        
        Args:
            chunks (List[str]): List of text chunks to save
            original_file (str): Original file path (used to create chunk filenames)
            output_dir (str): Directory to save chunks in
            
        Returns:
            List[str]: List of paths where chunks were saved
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(original_file))[0]
        
        # Save each chunk
        chunk_paths = []
        for i, chunk in enumerate(chunks, 1):
            chunk_filename = f"{base_name}_chunk_{i}.txt"
            chunk_path = os.path.join(output_dir, chunk_filename)
            
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk)
            
            chunk_paths.append(chunk_path)
        
        return chunk_paths
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Efficiently split text into chunks of approximately max_tokens tokens using line-based estimation.
        
        Args:
            text (str): The text to split
            
        Returns:
            List[str]: List of text chunks, each containing approximately max_tokens tokens
        """
        # Quick check if text needs splitting
        total_tokens = len(self.encoding.encode(text))
        if total_tokens <= self.max_tokens:
            return [text]
        
        # Split text into lines
        lines = text.split('\n')
        total_lines = len(lines)
        
        # Calculate average tokens per line
        avg_tokens_per_line = total_tokens / total_lines
        
        # Calculate approximate lines per chunk
        lines_per_chunk = int(self.max_tokens / avg_tokens_per_line)
        
        # Split into chunks
        chunks = []
        current_position = 0
        
        while current_position < total_lines:
            # Calculate end position for this chunk
            end_position = min(current_position + lines_per_chunk, total_lines)
            
            # Join lines for this chunk
            chunk = '\n'.join(lines[current_position:end_position])
            
            # Verify chunk size and adjust if needed
            chunk_tokens = len(self.encoding.encode(chunk))
            if chunk_tokens > self.max_tokens and end_position - current_position > 1:
                # If chunk is too big, reduce the number of lines proportionally
                reduction_factor = self.max_tokens / chunk_tokens
                new_lines = int((end_position - current_position) * reduction_factor)
                end_position = current_position + max(1, new_lines)
                chunk = '\n'.join(lines[current_position:end_position])
            
            chunks.append(chunk)
            current_position = end_position
        
        return chunks
    
    def get_all_file_paths(self, directory: str) -> List[str]:
        """
        Recursively get all file paths in a directory.
        
        Args:
            directory (str): The root directory to start searching from
            
        Returns:
            List[str]: A list of all file paths found
        """
        file_paths = []
        
        try:
            # Walk through the directory
            for root, dirs, files in os.walk(directory):
                # Add each file path to our list
                for file in files:
                    # Create full file path and append to list
                    file_path = os.path.join(root, file)
                    # Convert to relative path
                    relative_path = os.path.relpath(file_path, directory)
                    file_paths.append(relative_path)
                    
        except Exception as e:
            print(f"Error accessing directory {directory}: {str(e)}")
            return []
            
        return file_paths
    
    def get_file_info(self, file_paths: List[str], base_directory: str = "") -> Dict[str, Dict]:
        """
        Get file information including size and token count for each file.
        
        Args:
            file_paths (List[str]): List of file paths
            base_directory (str): Base directory to prepend to relative paths
            
        Returns:
            Dict[str, Dict]: Dictionary mapping file paths to their information (size and tokens)
        """
        file_info = {}
        
        for file_path in file_paths:
            try:
                full_path = os.path.join(base_directory, file_path)
                
                # Get file size
                file_size = os.path.getsize(full_path)
                
                # Get token count
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    token_count = len(self.encoding.encode(content))
                
                # Store all information in a nested dictionary
                file_info[file_path] = {
                    'size': file_size,
                    'tokens': token_count
                }
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                file_info[file_path] = {
                    'size': -1,
                    'tokens': -1
                }
                
        return file_info
    
    def process_directory(self, directory: str, chunks_dir: str = None) -> Dict[str, Dict]:
        """
        Process an entire directory, splitting files into chunks where needed.
        
        Args:
            directory (str): Directory to process
            chunks_dir (str, optional): Directory to save chunks in. Defaults to 'chunks' in parent directory.
            
        Returns:
            Dict[str, Dict]: Information about processed files and their chunks
        """
        if chunks_dir is None:
            # Go up one more directory level to save in Pitcher directory
            parent_dir = os.path.dirname(os.path.dirname(directory))
            chunks_dir = os.path.join(parent_dir, "chunks")
            
        files = self.get_all_file_paths(directory)
        file_info = self.get_file_info(files, directory)
        
        for file_path, info in file_info.items():
            if info['tokens'] > self.max_tokens:
                try:
                    full_path = os.path.join(directory, file_path)
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    chunks = self.split_into_chunks(content)
                    chunk_paths = self.save_chunks(chunks, full_path, chunks_dir)
                    
                    # Add chunk information to file_info
                    file_info[file_path]['chunks'] = [{
                        'path': path,
                        'tokens': len(self.encoding.encode(chunk))
                    } for chunk, path in zip(chunks, chunk_paths)]
                except Exception as e:
                    print(f"Error processing chunks for {file_path}: {str(e)}")
                    file_info[file_path]['chunks'] = []
        
        return file_info 