from dotenv import load_dotenv
from openai import OpenAI
import os
from pydantic import BaseModel
from pie import create_pie_chart
from bar import create_bar_chart
from line import create_line_chart
from flow import create_flowchart


load_dotenv()
OPENAI_KEY=os.getenv("OPENAI_API_KEY")

class bar(BaseModel):
    name:str
    x_values:list[float]
    y_values:list[float]
    x_label:str
    y_label:str

class pie(BaseModel):
    name:str
    values:list[float]
    labels:list [str]

class line(BaseModel):
    name:str
    x_values:list[float]
    y_values:list[float]
    x_label:str
    y_label:str

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

class output(BaseModel):
    pies: list[pie]
    bars: list[bar]
    lines: list[line]
    flows: list[flow]




messages=[{
             'role': 'system',
                'content': f""""Your job is to create charts based on a given document. The document contains all the central ideas
                about a particular tpoic/idea. we currently have the capabilities to make flowcharts, pie charts, bar charts, and line charts.
                Now I will provide you with the document and you return a list of all the charts that should be created with the appropriate required
                data.
                Make sure to fill in the correct values for each of the charts.
                For flow chart you will need to return a dictopry of nodes, connections, and node styles.
                here is an example 
                nodes = {{
                'start': 'Start',
                'input': 'Enter Data',
                'decision1': 'Is Data Valid?',
                'process1': 'Process Data',
                'db': 'Save to Database',
                'output': 'Display Results',
                'end': 'End'
            }}
            
            connections = [
                ('start', 'input'),
                ('input', 'decision1'),
                ('decision1', 'process1', 'Yes'),
                ('decision1', 'input', 'No'),
                ('process1', 'db'),
                ('db', 'output'),
                ('output', 'end')
            ]
            
            node_styles = {{
                'db': {{
                    'shape': 'cylinder',
                    'fillcolor': '#DDA0DD',
                    'style': 'filled'
                }},
                'input': {{
                    'shape': 'parallelogram',
                    'fillcolor': '#FAFAD2',
                    'style': 'filled'
                }},
                'output': {{
                    'shape': 'parallelogram',
                    'fillcolor': '#FAFAD2',
                    'style': 'filled'
                }}
            }}

                """
            }]



client=OpenAI(api_key=OPENAI_KEY)

with open("summary.txt") as f:
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

for graph in out.pies:
    create_pie_chart(graph.values, graph.labels, graph.name, "pies/" + graph.name+".png")
for graph in out.bars:
    create_bar_chart(graph.x_values, graph.y_values, None, graph.name, graph.x_label, graph.y_label, "bars/" + graph.name+".png")
for graph in out.lines:
    create_line_chart(graph.x_values, graph.y_values,None, graph.name, graph.x_label, graph.y_label, "lines/" + graph.name+".png")
for graph in out.flows:
    create_flowchart(graph, "flows/" + graph.name)