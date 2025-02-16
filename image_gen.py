from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langgraph.graph import Graph, START, END
import os
import time
from pyppeteer import launch
import asyncio

class ChartSpec(BaseModel):
    """Model for mermaid.js chart specification"""
    mermaid_code: str = Field(description="Complete mermaid.js code for the chart")
    html_template: str = Field(description="Complete HTML template including mermaid code")
    data_structure: Optional[str] = Field(description="Sample data structure if needed", default=None)

class ChartGenerationResult(BaseModel):
    """Model for the output of chart generation"""
    filename: str
    chart_spec: ChartSpec
    success: bool
    error_message: Optional[str] = None

class ImageGenerationOutput(BaseModel):
    """Model for the complete image generation process output"""
    generated_charts: List[ChartGenerationResult]
    png_files: List[str]  # List of generated PNG file paths
    timestamp: float 


async def generate_single_chart(
    filename: str,
    description: str,
    llm: ChatOpenAI,
    system_prompt: str,
    output_dir: str
) -> tuple[ChartGenerationResult, Optional[str]]:
    """
    Generates a single mermaid.js chart and converts it to PNG.
    
    Returns:
        tuple: (ChartGenerationResult, png_path or None)
    """
    try:
        start_time = time.time()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a mermaid.js visualization for this description: {description}"}
        ]
        print(f"starting image generation for {filename}")
        chart_spec = llm.invoke(messages)
        
        # Save HTML file
        html_filename = f"{os.path.splitext(filename)[0]}.html"
        html_path = os.path.join(output_dir, html_filename)
        
        with open(html_path, 'w') as f:
            f.write(chart_spec.html_template)
        
        # Convert to PNG
        png_filename = f"{os.path.splitext(filename)[0]}.png"
        png_path = os.path.join(output_dir, png_filename)
        
        success = False #await convert_mermaid_to_png(html_path, png_path)
        
        result = ChartGenerationResult(
            filename=filename,
            chart_spec=chart_spec,
            success=success,
            error_message=None if success else "PNG conversion failed"
        )
        print(f"mermaid html generation for {filename} done (Time taken: {time.time() - start_time })")
        
        return result, png_path if success else None
        
    except Exception as e:
        result = ChartGenerationResult(
            filename=filename,
            chart_spec=ChartSpec(
                mermaid_code="",
                html_template="",
            ),
            success=False,
            error_message=str(e)
        )
        return result, None
    
async def create_mermaid_charts_async(context: dict) -> dict:
    """
    Node function that generates mermaid.js charts in parallel based on image descriptions.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """
    You are an expert mermaid.js developer who creates clear, interactive visualizations.
    Your task is to generate complete mermaid.js code based on the provided description.

    Requirements for the mermaidChartSpec output:
    1. mermaid_code: Generate complete, working mermaid.js code that:
       - Uses mermaid.js
       - Is responsive and handles window resizing
       - Includes proper margins and padding
       - Uses appropriate scales and axes
       - Implements smooth transitions
       - Has clear variable names and comments
    2. html_template: Provide a complete HTML template that:
       - Includes necessary mermaid.js scripts
       - Has proper viewport settings
       - Includes the mermaid code
    3. data_structure: If the chart needs data, provide a sample data structure

    The code must be production-ready and able to run directly in a browser.
    """

    structured_llm = llm.with_structured_output(ChartSpec)
    
    # Create output directory
    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create tasks for parallel execution
    tasks = [
        generate_single_chart(
            filename,
            description,
            structured_llm,
            system_prompt,
            output_dir='images'
        )
        for filename, description in zip(
            context['slides']['image_placeholder_filenames'],
            context['slides']['image_placeholder_desc']
        )
    ]
    
    # Run all tasks in parallel
    results = await asyncio.gather(*tasks)
    
    # Separate results and PNG files
    generated_charts, png_files = zip(*results)
    png_files = [f for f in png_files if f is not None]
    
    # Update context with generation results
    context.update({
        'image_generation_results': ImageGenerationOutput(
            generated_charts=list(generated_charts),
            png_files=list(png_files),
            timestamp=time.time()
        ).model_dump()
    })
    
    return context

async def convert_mermaid_to_png(html_path: str, output_path: str, viewport: dict = None) -> bool:
    """
    Converts a mermaid.js visualization in HTML to a PNG file using Puppeteer.
    
    Args:
        html_path (str): Path to the HTML file containing the mermaid.js visualization
        output_path (str): Path where the PNG file should be saved
        viewport (dict, optional): Custom viewport settings. Defaults to 1200x800
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    if viewport is None:
        viewport = {'width': 1200, 'height': 800}
        

    browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
    # Create new page
    page = await browser.newPage()
    
    # Set viewport
    await page.setViewport(viewport)
    
    # Load HTML file
    await page.goto(f'file://{os.path.abspath(html_path)}')
    
    # Wait for mermaid transitions and animations to complete
    await asyncio.sleep(1)
    
    # Make sure the chart container is visible
    await page.waitForSelector('#chart')
    
    # Additional wait to ensure chart is fully rendered
    await asyncio.sleep(0.5)
    
    # Take screenshot
    await page.screenshot({'path': output_path, 'type': 'png'})
    
    # Close browser
    await browser.close()
    
    return True
        
    # except Exception as e:
    #     print(f"Error converting {html_path} to PNG: {str(e)}")
    #     return False

def create_mermaid_charts(context: dict) -> dict:
    """
    Synchronous wrapper for the asynchronous chart generation function.
    """
    return asyncio.get_event_loop().run_until_complete(
        create_mermaid_charts_async(context)
    )