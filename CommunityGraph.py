import networkx as nx
import json
from pyvis.network import Network
import community as community_louvain


extreme_optimization = True

# Load your dataset
with open(r"mention_networks\network_mega_merge.json", "r", encoding="utf-8") as f:
    edges = json.load(f)

# Build the graph
G = nx.Graph()
G.add_edges_from(edges)

# Detect communities with Louvain
partition = community_louvain.best_partition(G)

# Create Pyvis network
net = Network(
    height="1000px",
    width="100%",
    notebook=False,
    bgcolor="#222222",
    font_color="white",
    filter_menu=True  # enables GUI
)

# Use ForceAtlas2 for better performance with large graphs
net.force_atlas_2based(gravity=-30, central_gravity=0.01, damping=0.4)

# Add nodes and edges with colors for communities
for node in G.nodes():
    comm = partition[node] 
    net.add_node(
        node, 
        label=node,
         title=f"Account: {node}    Community: {comm}",
        color=f"hsl({(partition[node] * 57) % 360}, 80%, 60%)",
        size = 8,
        community=comm
    )


# Disable smooth edges (optimization)
for edge in G.edges():
    net.add_edge(edge[0], edge[1], smooth=False)


net.set_options("""
{
  "physics": {
    "enabled": true,
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -30,
      "centralGravity": 0.01,
      "damping": 0.4,
      "springLength": 100,
      "springConstant": 0.02
    },
    "stabilization": {
      "enabled": true,
      "iterations": 100,
      "updateInterval": 25,
      "onlyDynamicEdges": false,
      "fit": true
    }
  }
}
""")




# Save to and open in browser
import webbrowser

html_path = "x_community_graph.html"
net.write_html(html_path)

webbrowser.open(html_path)

