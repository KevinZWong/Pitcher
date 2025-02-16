import re
import json

def extract_image_urls_and_descriptions(markdown_file, json_file):
    # Read markdown file
    with open(markdown_file, 'r') as f:
        markdown_content = f.read()
    
    # Read JSON file
    with open(json_file, 'r') as f:
        graph_data = json.load(f)
    
    # Create a dictionary mapping filepaths to descriptions
    filepath_to_description = {
        item['filepath']: {
            'description': item['description']
        }
        for item in graph_data
    }
    
    # Regular expression to find image URLs
    # This pattern matches markdown image syntax: ![alt](url)
    image_pattern = r'!\[.*?\]\((.*?)\)'
    
    # Find all image URLs
    image_urls = re.findall(image_pattern, markdown_content)
    
    # Create result string
    result = "Image URLs and Descriptions:\n\n"
    
    for url in image_urls:
        # Get description and type from JSON if it exists
        if url in filepath_to_description:
            graph_info = filepath_to_description[url]
            result += f"File: {url}\n"
            result += f"Description: {graph_info['description']}\n"
            result += "-" * 50 + "\n"
        else:
            result += f"File: {url}\n"
            result += "Description: No description available\n"
            result += "-" * 50 + "\n"
    
    return result

# Example usage:
if __name__ == "__main__":
    try:
        result = extract_image_urls_and_descriptions('../presentation.md', '../extracted_images/combined_metadata.json')
        print(result)
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except Exception as e:
        print(f"Error: {e}")