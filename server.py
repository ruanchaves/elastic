from elastic import Graph, convert_graph
from flask import Flask, render_template
import json
app = Flask(__name__)

@app.route('/<depth>/<query>')
def main(query=None, depth=1):
    G = Graph()
    G.build_graph(query, int(depth))
    output = convert_graph(G.nodes, G.edges)
    return render_template('query.html', query=query, nodes=json.dumps(output['nodes']), edges=json.dumps(output['edges']))