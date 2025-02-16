import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

def create_line_chart(x_values, y_values, labels=None, title="Line Chart",
                     xlabel="X Axis", ylabel="Y Axis", output_file="line_chart.png",
                     colors=None, markers=None, line_styles=None, show_grid=True):
    """
    Create a line chart and save it as a PNG file.
    
    Parameters:
    x_values: list of x values, or list of lists for multiple lines
    y_values: list of y values, or list of lists for multiple lines
    labels: list of labels for each line (optional)
    title: chart title (default: "Line Chart")
    xlabel: x-axis label (default: "X Axis")
    ylabel: y-axis label (default: "Y Axis")
    output_file: output file name (default: "line_chart.png")
    colors: list of colors for lines (optional)
    markers: list of marker styles for data points (optional)
    line_styles: list of line styles (optional)
    show_grid: boolean to show grid (default: True)
    """
    
    plt.figure(figsize=(12, 6))
    
    # Convert single line data to list of lines format
    if not isinstance(y_values[0], (list, tuple, np.ndarray)):
        x_values = [x_values]
        y_values = [y_values]
    
    # Default settings if not provided
    if labels is None:
        labels = [f'Line {i+1}' for i in range(len(y_values))]
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(y_values)))
    if markers is None:
        markers = ['o'] * len(y_values)
    if line_styles is None:
        line_styles = ['-'] * len(y_values)
    
    # Plot each line
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        plt.plot(x, y, 
                label=labels[i],
                color=colors[i],
                marker=markers[i],
                linestyle=line_styles[i],
                linewidth=2,
                markersize=6)
    
    # Customize the chart
    plt.title(title, pad=20)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Add legend
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add grid
    if show_grid:
        plt.grid(True, linestyle='--', alpha=0.7)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    # Open the saved image to get its dimensions
    with Image.open(output_file) as img:
        width, height = img.size
    plt.close()
    
    return width, height

# Example usage:
if __name__ == "__main__":
    # Single line example
    x = np.arange(0, 10, 0.5)
    y = np.sin(x)
    
    create_line_chart(x, y,
                     title="Simple Sine Wave",
                     xlabel="X",
                     ylabel="sin(x)",
                     output_file="sine_wave.png")
    
    # Multiple lines example
    x = np.arange(0, 10)
    y1 = x**2
    y2 = x**1.5
    y3 = x
    
    create_line_chart([x, x, x],
                     [y1, y2, y3],
                     labels=["Quadratic", "Power 1.5", "Linear"],
                     title="Multiple Functions",
                     xlabel="X",
                     ylabel="Y",
                     output_file="multiple_functions.png",
                     markers=['o', 's', '^'],
                     line_styles=['-', '--', ':'])