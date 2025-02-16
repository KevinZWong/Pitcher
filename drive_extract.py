import time
import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pickle
import shutil

class DriveDownloader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.creds = None
        self.service = None

    def authenticate(self):
        """Handles authentication with Google Drive API."""
        # Check if we have valid credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If credentials are invalid or don't exist, let's create them
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def extract_folder_id(self, folder_url):
        """Extracts folder ID from Google Drive URL."""
        pattern = r'(?:folders/|id=)([a-zA-Z0-9-_]+)'
        match = re.search(pattern, folder_url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Google Drive folder URL")

    def list_files(self, folder_id):
        """Lists all files in the specified folder."""
        results = []
        page_token = None
        
        while True:
            try:
                query = f"'{folder_id}' in parents and trashed = false"
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType)',
                    pageToken=page_token
                ).execute()

                results.extend(response.get('files', []))
                page_token = response.get('nextPageToken')

                if not page_token:
                    break

            except Exception as e:
                print(f"An error occurred: {e}")
                break

        return results

    def download_file(self, file_id, file_name, download_path):
        """Downloads a single file from Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Downloading {file_name}: {int(status.progress() * 100)}%")

            file_handle.seek(0)
            
            # Create full path for file
            full_path = os.path.join(download_path, file_name)
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the file
            with open(full_path, 'wb') as f:
                f.write(file_handle.read())
                
            print(f"Downloaded: {file_name}")
            return True

        except Exception as e:
            print(f"Error downloading {file_name}: {e}")
            return False

    def download_folder(self, folder_url, download_path):
        """Downloads all files from a Google Drive folder."""
        try:
            # Authenticate if not already done
            if not self.service:
                self.authenticate()
            # Empty the download path
            if os.path.exists(download_path):
                shutil.rmtree(download_path)
            # Extract folder ID from URL
            folder_id = self.extract_folder_id(folder_url)
            print("The folder_id is ", folder_id)
            # Create download directory if it doesn't exist
            os.makedirs(download_path, exist_ok=True)
            
            # Get list of files in the folder
            files = self.list_files(folder_id)
            
            if not files:
                print("No files found in the folder.")
                return
            
            # Download each file
            successful_downloads = 0
            for file in files:
                if self.download_file(file['id'], file['name'], download_path):
                    successful_downloads += 1
            
            print(f"\nDownload complete! Successfully downloaded {successful_downloads} of {len(files)} files.")

        except KeyError as e:
            print(f"An error occurred: {e}")

def main():
    # Example usage
    downloader = DriveDownloader()
    folder_url = input("Enter the Google Drive folder URL: ")
    download_path = input("Enter the download path: ")
    
    downloader.download_folder(folder_url, download_path)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Time taken: ", time.time() - start_time)