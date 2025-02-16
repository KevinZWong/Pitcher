import subprocess
import os
from pathlib import Path
import shutil
import gdown

def download_from_github(repo_url: str, output_dir: str = "code_data"):
    """
    Clone a GitHub repository to the specified directory
    
    Args:
        repo_url: URL of the GitHub repository
        output_dir: Directory to save the code (default: code_data)
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    print(f"Cloning repository: {repo_url}")
    print(f"Saving to: {output_dir}")
    
    try:
        # Remove directory if it already exists
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, output_dir], check=True)
        print("\nRepository cloned successfully!")
        
    except Exception as e:
        print(f"Error cloning repository: {str(e)}")

def download_from_gdrive_folder(folder_url: str, output_dir: str = "text_data"):
    """
    Download all files from a public Google Drive folder
    
    Args:
        folder_url: URL of the public Google Drive folder
        output_dir: Directory to save downloaded files (default: text_data)
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    print(f"Downloading files from: {folder_url}")
    print(f"Saving to: {output_dir}")
    
    try:
        # Download all files from the folder
        gdown.download_folder(
            url=folder_url,
            output=output_dir,
            quiet=False,
            use_cookies=False
        )
        print("\nDownload completed successfully!")
        
    except Exception as e:
        print(f"Error downloading files: {str(e)}")

if __name__ == "__main__":

    folder_url = "https://drive.google.com/drive/folders/1HohSxiUb2C0IKWfVXgLFhrQKs-v26M20?usp=sharing"
    repo_url = "https://github.com/KevinZWong/Mapling"
    # download_from_gdrive_folder(folder_url)
    download_from_github(repo_url)







