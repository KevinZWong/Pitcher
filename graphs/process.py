import json
from dotenv import load_dotenv
from openai import OpenAI
import os
from pydantic import BaseModel
from graphs.pie import create_pie_chart
from graphs.bar import create_bar_chart
from graphs.line import create_line_chart
from graphs.flow import create_flowchart


load_dotenv()
OPENAI_KEY=os.getenv("OPENAI_API_KEY")

class bar(BaseModel):
    name:str
    x_values:list[float]
    y_values:list[float]
    x_label:str
    y_label:str
    description:str

class pie(BaseModel):
    name:str
    values:list[float]
    labels:list [str]
    description:str

class line(BaseModel):
    name:str
    x_values:list[float]
    y_values:list[float]
    x_label:str
    y_label:str
    description:str

class connection(BaseModel):
    from_node:str
    to_node:str

class node(BaseModel):
    name:str
    label:str   

class flow(BaseModel):
    name:str
    nodes:list[node]
    connections:list[connection]
    description:str

class output(BaseModel):
    pies: list[pie]
    bars: list[bar]
    lines: list[line]
    flows: list[flow]


def image_gen():
    messages=[{
                'role': 'system',
                    'content': f""""Your job is to create charts based on a given document. The document contains all the central ideas
                    about a particular tpoic/idea. we currently have the capabilities to make flowcharts, pie charts, bar charts, and line charts.
                    Now I will provide you with the document and you return a list of all the charts that should be created with the appropriate required
                    data.
                    Make sure to fill in the correct values for each of the charts.
                    Do not use spaces between names.
                    Make as many meaningful graphs as you can
                    Include a deailted description what each image represents
                    """
                }]



    client=OpenAI(api_key=OPENAI_KEY)

    with open("extract/summary/text_summary.txt") as f:
        document=f.read()
    formatted_user_query = f"""
    This is the document:\n
    {document}

    """
    messages.append(
        {
            'role': 'user',
            'content': formatted_user_query
        })
    routput = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=output
    )
    out =  routput.choices[0].message.parsed
    print(out)

    combined_metadata = [] 
        

    for graph in out.pies:
        create_pie_chart(graph.values, graph.labels, graph.name, "graphs/pies/" + graph.name+".png")
        combined_metadata.append({
            "type": "pie",
            "filepath": "graphs/pies/" + graph.name +".png",
            # "values": graph.values,
            # "labels": graph.labels,
            "description": graph.description
        })
    for graph in out.bars:
        create_bar_chart(graph.x_values, graph.y_values, None, graph.name, graph.x_label, graph.y_label, "graphs/bars/" + graph.name+".png")
        combined_metadata.append({
            "type": "bar",
            "filepath": "graphs/bars/" + graph.name +".png",
            # "x_values": graph.x_values,
            # "y_values": graph.y_values,
            # "x_label": graph.x_label,
            # "y_label": graph.y_label,
            "description": graph.description
        })
    for graph in out.lines:
        create_line_chart(graph.x_values, graph.y_values,None, graph.name, graph.x_label, graph.y_label, "graphs/lines/" + graph.name+".png")
        combined_metadata.append({
            "type": "line",
            "filepath": "graphs/lines/" + graph.name +".png",
            # "x_values": graph.x_values,
            # "y_values": graph.y_values,
            # "x_label": graph.x_label,
            # "y_label": graph.y_label,
            "description": graph.description
        })
    for graph in out.flows:
        create_flowchart(graph, "graphs/flows/" + graph.name)
        combined_metadata.append({
            "type": "flow",
            "filepath": "graphs/flows/" + graph.name +".png",
            "description": graph.description
        })

    json_file_path = "extracted_images/combined_metadata.json"
    existing_data = []

    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            # Handle empty or invalid JSON file

            existing_data = []

    # If gen_images doesn't exist in the data, create it
    print(existing_data)
    # Append new combined_metadata to gen_images
    existing_data.extend(combined_metadata)

    # Write back to the file
    with open(json_file_path, 'w') as f:
        json.dump(existing_data, f, indent=2)

#image_gen