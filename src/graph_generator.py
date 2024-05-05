from graphviz import Source

def create_graph_file(graph_data, output_file_name):
    graph = Source(graph_data)
    graph.render(output_file_name, format='png', cleanup=True)
    return (output_file_name + ".png")