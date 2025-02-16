import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('Agg')
from PIL import Image
import os
import time
def create_bar_chart(x_values, y_values, labels=None, title="Bar Chart", 
                    xlabel="X Axis", ylabel="Y Axis", output_file="bar_chart.png"):
    """
    Create a bar chart and save it as a PNG file.
    
    Parameters:
    x_values: list/array of x-coordinates
    y_values: list/array of y-coordinates
    labels: list of labels for each bar (optional)
    title: chart title (default: "Bar Chart")
    xlabel: x-axis label (default: "X Axis")
    ylabel: y-axis label (default: "Y Axis")
    output_file: output file name (default: "bar_chart.png")
    """
    
    # Create figure and axis
    plt.figure(figsize=(10, 6))
    
    # Create bars
    bars = plt.bar(x_values, y_values)
    
    # Add labels if provided
    if labels:
        plt.xticks(x_values, labels, rotation=45, ha='right')
    
    # Add title and axis labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:,.0f}',
                ha='center', va='bottom')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join("/Users/swastikagrawal/Documents/TreeHacks/Pitcher/pitcher/public",output_file)
    fig = plt.gcf()  # Get current figure
    width, height = fig.get_size_inches()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    # time.sleep(1)
    # with Image.open(output_path) as img:
    #     width, height = img.size
    plt.close()
    return width, height

# Example usage:
if __name__ == "__main__":
    # Sample data
    x = np.arange(5)
    y = [23, 45, 56, 78, 32]
    labels = ['A', 'B', 'C', 'D', 'E']
    
    create_bar_chart(x, y, labels, 
                     title="Sample Bar Chart",
                     xlabel="Categories",
                     ylabel="Values")