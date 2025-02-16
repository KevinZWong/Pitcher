def generate_slides(prompt, content):
    """Mock function for marp_slides.generate_slides"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Presentation</title>
        <style>
            .slide {{
                height: 100vh;
                padding: 2em;
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        <div class="slide">
            <h1>Generated Presentation</h1>
            <p>Prompt: {prompt}</p>
        </div>
        <div class="slide">
            <h2>Content Overview</h2>
            <pre>{content[:500]}...</pre>
        </div>
    </body>
    </html>
    """
    return html_template

def process_code_directory(directory_path):
    """Mock function for describe.process_directory"""
    return [
        "Mock code analysis:",
        f"Analyzed directory: {directory_path}",
        "Found: Sample Code Structure",
        "- src/",
        "  - main.py",
        "  - utils.py",
        "Sample code content would be processed here"
    ]

def extract_text_from_pdf(pdf_path):
    """Mock function for extract_text_code.main"""
    return [
        "Mock PDF extraction:",
        f"Extracted from: {pdf_path}",
        "Sample PDF content",
        "Chapter 1: Introduction",
        "This is sample text that would be extracted from the PDF",
        "Some code examples:",
        "```python",
        "def example():",
        "    return 'Hello World'",
        "```"
    ]

# Test function to demonstrate usage
def test_runner():
    print("Testing mock functions...")
    
    # Test PDF extraction
    pdf_result = extract_text_from_pdf("sample.pdf")
    print("\nPDF Extraction Result:")
    print("\n".join(pdf_result))
    
    # Test code directory processing
    code_result = process_code_directory("/path/to/code")
    print("\nCode Analysis Result:")
    print("\n".join(code_result))
    
    # Test slide generation
    combined_content = "\n".join(pdf_result + code_result)
    slides = generate_slides("Create a technical presentation", combined_content)
    
    # Save the test output
    with open("pitcher/public/slides.html", "w", encoding="utf-8") as f:
        f.write(slides)
    print("\nSlides generated and saved to slides.html")

if __name__ == "__main__":
    test_runner()
