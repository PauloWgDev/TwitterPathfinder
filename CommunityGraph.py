import networkx as nx
import json
from pyvis.network import Network
import community as community_louvain


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
    height="900px",
    width="100%",
    notebook=False,
    bgcolor="#222222",
    font_color="white",
    filter_menu=True  # this enables the built-in search/filter UI
)

net.barnes_hut()  # Force-directed layout

# Add nodes and edges with colors for communities
for node in G.nodes():
    net.add_node(
        node, 
        label=node,
        title=f"Account: {node}<br>Community: {partition[node]}",
        color=f"hsl({(partition[node] * 57) % 360}, 80%, 60%)"
    )

for edge in G.edges():
    net.add_edge(edge[0], edge[1])

# Save to and open in browser
import webbrowser

html_path = "x_community_graph.html"
net.write_html(html_path)

webbrowser.open(html_path)

