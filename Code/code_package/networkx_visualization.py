#Visualize using networkx (avoiding plotly's limits)

import networkx as nx
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from lib import path_lib

colors = ['b', 'g', 'r', 'k', 'c', 'm', 'y', 'w']

def draw_graph(edges, groups, hard_edges, hard_nodes, path, draw_nodes=False, draw_edges=False, draw_hard_edges=False, draw_hard_nodes=False):
	print('Drawing {} graph:'.format(path_lib.get_filename_without_extension(path)))
	G = nx.Graph()
	for edge in edges:
		G.add_edge(edge['source'], edge['target'], weight=edge['value'])
	pos = nx.spring_layout(G)

	if draw_nodes:
		print('\tDrawing nodes...')
		group_names = list(groups.keys())
		group_names.sort()
		for group in group_names:
			nx.draw_networkx_nodes(G, pos, nodelist=groups[group], node_color=colors[group], node_size=500, alpha=0.8)

	if draw_hard_nodes:
		print('\tDrawing hard nodes...')
		group_names = list(hard_nodes.keys())
		group_names.sort()
		for group in group_names:
			nx.draw_networkx_nodes(G, pos, nodelist=hard_nodes[group], node_color=colors[group], node_size=500, alpha=0.8)

	if draw_edges:
		print('\tDrawing edges...')
		nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)

	if draw_hard_edges:
		print('\tDrawing hard edges...')
		hard_edges = [(x['source'], x['target']) for x in hard_edges]
		nx.draw_networkx_edges(G, pos, edgelist=hard_edges, width=3, alpha=0.8, edge_color='r')

	plt.axis('off')
	plt.savefig(path)
	plt.clf()


def draw_original_graph(edges, groups, hard_edges, hard_nodes, base_path):
	draw_graph(edges, groups, hard_edges, hard_nodes, os.path.join(base_path, 'original.png'), draw_nodes=True, draw_edges=True)

def draw_overlayed_graph(edges, groups, hard_edges, hard_nodes, base_path):
	draw_graph(edges, groups, hard_edges, hard_nodes, os.path.join(base_path, 'overlayed.png'), draw_nodes=True, draw_edges=True, draw_hard_edges=True)

def draw_hard_edge_graph(edges, groups, hard_edges, hard_nodes, base_path):
	draw_graph(edges, groups, hard_edges, hard_nodes, os.path.join(base_path, 'hard_edges.png'), draw_nodes=True, draw_hard_edges=True)

def draw_hard_graph(edges, groups, hard_edges, hard_nodes, base_path):
	draw_graph(edges, groups, hard_edges, hard_nodes, os.path.join(base_path, 'hard.png'), draw_hard_nodes=True, draw_hard_edges=True)

#Runs the networkx visualization given a list of nodes, a list of edges, and a list of hard-edges
def visualize(nodes, edges, groups, base_path, hard_edges=None):
	print("Running visualization protocol...")

	visible_nodes = []
	for e in edges:
		visible_nodes.append(e['target'])
		visible_nodes.append(e['source'])
	visible_nodes = list(set(visible_nodes))
	for group in groups:
		g = groups[group]
		for ii in range(len(g)-1, -1, -1):
			if not g[ii] in visible_nodes:
				del g[ii]
		groups[group] = g

	hard_nodes = []
	for e in hard_edges:
		hard_nodes.append(e['source'])
		hard_nodes.append(e['target'])
	hard_nodes = list(set(hard_nodes))
	hard_groups = {}
	for group in groups:
		g = groups[group]
		ng = []
		for v in g:
			if v in hard_nodes:
				ng.append(v)
		hard_groups[group] = ng

	draw_original_graph(edges, groups, hard_edges, hard_groups, base_path)
	draw_overlayed_graph(edges, groups, hard_edges, hard_groups, base_path)
	draw_hard_edge_graph(edges, groups, hard_edges, hard_groups, base_path)
	draw_hard_graph(edges, groups, hard_edges, hard_groups, base_path)