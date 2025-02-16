from pydantic import BaseModel
from typing import List
from graphviz import Digraph

class Connection(BaseModel):
   from_node: str 
   to_node: str

class Node(BaseModel):
   name: str
   label: str

class Flow(BaseModel):
   name: str
   nodes: List[Node]
   connections: List[Connection]

def create_flowchart(flow: Flow, filename="flowchart", direction='TB'):
   """
   Create a flowchart from a Flow object.
   
   Parameters:
   flow: Flow object containing nodes and connections
   filename: output filename (without extension)
   direction: graph direction ('TB', 'LR', 'RL', 'BT')
   """
   
   # Initialize graph
   dot = Digraph()
   dot.attr(rankdir=direction)
   
   # Default styles for different node types
   default_styles = {
       'start': {'shape': 'oval', 'fillcolor': '#90EE90', 'style': 'filled'},
       'end': {'shape': 'oval', 'fillcolor': '#FFB6C1', 'style': 'filled'},
       'decision': {'shape': 'diamond', 'fillcolor': '#87CEEB', 'style': 'filled'},
       'process': {'shape': 'box', 'fillcolor': 'white', 'style': 'filled'}
   }
   
   # Add nodes
   for node in flow.nodes:
       # Determine node style
       style = {}
       if node.name.lower().startswith('decision'):
           style = default_styles['decision']
       elif node.name.lower().startswith('start'):
           style = default_styles['start']
       elif node.name.lower().startswith('end'):
           style = default_styles['end']
       else:
           style = default_styles['process']
       
       # Create node
       dot.node(node.name, node.label, **style)
   
   # Add connections
   for conn in flow.connections:
       dot.edge(conn.from_node, conn.to_node)
   
   # Save the flowchart
   dot.render(filename, format='png', cleanup=True)

# Example usage
if __name__ == "__main__":
   # Create a flow using the Pydantic models
   flow = Flow(
       name="example_flow",
       nodes=[
           Node(name='start', label='Start'),
           Node(name='input', label='Enter Data'),
           Node(name='decision1', label='Is Data Valid?'),
           Node(name='process1', label='Process Data'),
           Node(name='db', label='Save to Database'),
           Node(name='output', label='Display Results'),
           Node(name='end', label='End')
       ],
       connections=[
           Connection(from_node='start', to_node='input'),
           Connection(from_node='input', to_node='decision1'),
           Connection(from_node='decision1', to_node='process1'),
           Connection(from_node='decision1', to_node='input'),
           Connection(from_node='process1', to_node='db'),
           Connection(from_node='db', to_node='output'),
           Connection(from_node='output', to_node='end')
       ]
   )
   
   create_flowchart(flow, 'flowchart')