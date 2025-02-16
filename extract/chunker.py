import os
from typing import List, Dict, Tuple
import tiktoken
from pathlib import Path
import PyPDF2
import io
import json
import yaml
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import logging

class TextChunker:
    def __init__(self, model: str = "gpt-4o-mini", max_tokens: int = 20000):
        """
        Initialize the TextChunker with model and token settings.
        
        Args:
            model (str): The model to use for tokenization
            max_tokens (int): Maximum number of tokens per chunk
        """
        self.model = model
        self.max_tokens = max_tokens
        self.encoding = tiktoken.encoding_for_model(model)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_file_type(self, file_path: str) -> str:
        """
        Determine the type of file based on its extension.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Type of the file ('pdf', 'code', 'markup', 'data', 'text')
        """
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'pdf':
            return 'pdf'
        elif ext in ['html', 'htm', 'xml', 'svg']:
            return 'markup'
        elif ext in ['json', 'yaml', 'yml', 'toml']:
            return 'data'
        elif ext in ['py', 'js', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 
                    'swift', 'kt', 'scala', 'm', 'ts', 'jsx', 'tsx', 'css', 'scss', 
                    'sass', 'less', 'sh', 'bash', 'zsh', 'fish', 'sql', 'graphql']:
            return 'code'
        else:
            return 'text'

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from various file types.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Extracted text content
        """
        try:
            file_type = self.get_file_type(file_path)
            
            if file_type == 'pdf':
                # Handle PDF file
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            
            elif file_type == 'markup':
                # Handle HTML, XML, SVG
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if file_path.lower().endswith(('.html', '.htm')):
                        soup = BeautifulSoup(content, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        return soup.get_text(separator=' ', strip=True)
                    elif file_path.lower().endswith(('.xml', '.svg')):
                        tree = ET.parse(file_path)
                        return ' '.join(tree.itertext())
            
            elif file_type == 'data':
                # Handle JSON, YAML
                with open(file_path, 'r', encoding='utf-8') as file:
                    if file_path.lower().endswith('.json'):
                        data = json.load(file)
                        return json.dumps(data, indent=2)
                    elif file_path.lower().endswith(('.yaml', '.yml')):
                        data = yaml.safe_load(file)
                        return yaml.dump(data, default_flow_style=False)
                    else:
                        return file.read()
            
            else:
                # Handle all other text-based files
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
                    
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return ""

    def save_chunk(self, content: str, chunk_number: int, output_dir: str) -> str:
        """Save a single chunk to a file."""
        os.makedirs(output_dir, exist_ok=True)
        chunk_path = os.path.join(output_dir, f"combined_chunk_{chunk_number}.txt")
        
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
        return chunk_path
    
    def process_directory(self, directory: str, chunks_dir: str = None) -> Dict[str, Dict]:
        """
        Process all files in directory, combining small files and splitting large ones
        to create chunks close to max_tokens size.
        """
        if chunks_dir is None:
            chunks_dir = os.path.join(directory, "..", "chunks")



        # First, get all text content and token counts
        all_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith((
                    # Documents and text
                    '.txt', '.pdf', '.md', '.rst', '.rtf',
                    # Source code
                    '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift',
                    '.kt', '.scala', '.m', '.ts', '.jsx', '.tsx',
                    # Web and markup
                    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.xml', '.svg',
                    # Configuration and data
                    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
                    '.properties', '.env',
                    # Shell scripts
                    '.sh', '.bash', '.zsh', '.fish',
                    # Other
                    '.sql', '.graphql', '.log'
                )):
                    file_path = os.path.join(root, file)
                    content = self.extract_text_from_file(file_path)
                    tokens = self.encoding.encode(content)
                    all_files.append({
                        'path': file_path,
                        'content': content,
                        'tokens': len(tokens),
                        'type': self.get_file_type(file_path)
                    })

        # Sort files by token count for efficient combining
        all_files.sort(key=lambda x: x['tokens'])
        
        # Initialize result tracking
        file_info = {}
        current_chunk = ""
        current_tokens = 0
        chunk_number = 1
        source_files = []

        # Process all files
        for file in all_files:
            file_tokens = file['tokens']
            relative_path = os.path.relpath(file['path'], directory)
            
            # Initialize file info
            file_info[relative_path] = {
                'size': os.path.getsize(file['path']),
                'tokens': file_tokens,
                'type': file['type'],
                'chunks': []
            }

            # If file is larger than max_tokens, split it
            if file_tokens > self.max_tokens:
                tokens = self.encoding.encode(file['content'])
                
                for i in range(0, len(tokens), self.max_tokens):
                    chunk_tokens = tokens[i:min(i + self.max_tokens, len(tokens))]
                    chunk_text = self.encoding.decode(chunk_tokens)
                    chunk_path = self.save_chunk(chunk_text, chunk_number, chunks_dir)
                    
                    file_info[relative_path]['chunks'].append({
                        'path': chunk_path,
                        'tokens': len(chunk_tokens)
                    })
                    chunk_number += 1
                
                continue

            # If adding this file would exceed max_tokens, save current chunk and start new one
            if current_tokens + file_tokens > self.max_tokens and current_chunk:
                chunk_path = self.save_chunk(current_chunk, chunk_number, chunks_dir)
                
                # Record chunk info for all source files
                for src_file in source_files:
                    if src_file not in file_info:
                        file_info[src_file] = {'chunks': []}
                    file_info[src_file]['chunks'].append({
                        'path': chunk_path,
                        'tokens': current_tokens
                    })
                
                # Reset for next chunk
                current_chunk = ""
                current_tokens = 0
                source_files = []
                chunk_number += 1

            # Add file content to current chunk
            current_chunk += f"\n--- {relative_path} ---\n{file['content']}\n"
            current_tokens += file_tokens
            source_files.append(relative_path)

        # Save any remaining content
        if current_chunk:
            chunk_path = self.save_chunk(current_chunk, chunk_number, chunks_dir)
            for src_file in source_files:
                if src_file not in file_info:
                    file_info[src_file] = {'chunks': []}
                file_info[src_file]['chunks'].append({
                    'path': chunk_path,
                    'tokens': current_tokens
                })
        return file_info 