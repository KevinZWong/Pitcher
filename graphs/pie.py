import matplotlib.pyplot as plt

def create_pie_chart(values, labels, title="Pie Chart", output_file="pie_chart.png", 
                     colors=None, show_percentages=True, show_legend=True):
    """
    Create a pie chart and save it as a PNG file.
    
    Parameters:
    values: list/array of values for each slice
    labels: list of labels for each slice
    title: chart title (default: "Pie Chart")
    output_file: output file name (default: "pie_chart.png")
    colors: list of colors for slices (optional)
    show_percentages: bool to show percentage labels (default: True)
    show_legend: bool to show legend (default: True)
    """
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Calculate percentages for labels
    total = sum(values)
    percentages = [f'{(value/total)*100:.1f}%' for value in values]
    
    # Create autopct function to show both value and percentage
    def make_autopct(values, percentages):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{val:,}\n({percentages[int(round(pct*len(percentages)/100.0-0.5))]})' if show_percentages else ''
        return my_autopct
    
    # Create pie chart
    plt.pie(values, 
            labels=labels if not show_legend else None,
            colors=colors,
            autopct=make_autopct(values, percentages),
            startangle=90)
    
    # Add title
    plt.title(title)
    
    # Add legend
    if show_legend:
        plt.legend(labels, title="Categories", 
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Ensure the pie chart is circular
    plt.axis('equal')
    
    # Adjust layout to prevent cutoff
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

# Example usage:
if __name__ == "__main__":
    # Sample data
    values = [35, 25, 20, 15, 5]
    labels = ['Product A', 'Product B', 'Product C', 'Product D', 'Other']
    
    # Optional custom colors
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    
    create_pie_chart(values, labels,
                    title="Sales Distribution",
                    output_file="sales_distribution.png",
                    colors=colors)