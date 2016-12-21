#Collects all the results

import os
import sys
import random
import json
import copy

from lib import const_lib
from lib import path_lib
from lib import arg_lib
from lib import console_lib

global_paths = const_lib.load_global_paths()

def _setup_grouping_by_count(matrix, num_groups):
	nodes = {}
	N = len(matrix)
	group_sizes = int(N/num_groups)

	for ii in range(num_groups):
		if ii < num_groups - 1:
			for jj in range(ii*group_sizes, (ii+1)*group_sizes):
				nodes[jj] = ii
		else:
			for jj in range(ii*group_sizes, len(matrix)):
				nodes[jj] = ii
	return nodes

def _load_matrix_data(file_path):
	matrix = []
	entries = 0
	with open(file_path, 'r') as f:
		lines = f.readlines()
	for ii in range(0, len(lines)):
		line = lines[ii].strip().split('\t')
		row = []
		for jj in range(0, len(line)):
			row.append(float(line[jj]))
			entries += 1
		matrix.append(row)
	return matrix, entries

#Loads the sparse edges
#
#@input sparse_file<string>: path to sparse file
#@return sparse_edges<list<dict>>: list of sparse edges
#
def _load_sparse_edges(sparse_file):
	sparse_edges = []
	with open(sparse_file, 'r') as f:
		edges = f.readlines()
	for edge in edges:
		edge = edge.strip()
		if edge != '':
			edge = edge.split('\t')
			e = {'source': int(edge[0]), 'target': int(edge[1])}
			sparse_edges.append(e)
	return sparse_edges

def _run(data_path):
	output_file = os.path.join(data_path, 'results.txt')
	graph_base = os.path.join(data_path, 'graphs')
	results = []
	graphs = path_lib.get_all_files_in_directory(graph_base)
	for graph in graphs:
		if 'reddit' in graph and 'g' in graph and 'n' in graph and 'cro' in graph and 'con' in graph:
			print(graph)
			result = {}
			settings = graph.split('_')
			result['name'] = graph
			result['groups'] = int(settings[1].replace('g', ''))
			result['nodes'] = int(settings[2].replace('n', ''))
			result['cross_connection_percentage'] = float(settings[3].replace('cro', ''))/10
			result['intra_connection_percentage'] = float(settings[4].replace('con', ''))/10
			graph_path = os.path.join(graph_base, graph)
			Adj, entries = _load_matrix_data(os.path.join(graph_path, 'adjacency.txt'))
			sparse = _load_sparse_edges(os.path.join(graph_path, 'sparse.txt'))
			nodes = _setup_grouping_by_count(Adj, result['groups'])

			t_e = 0
			c_e = 0
			i_e = 0

			for ii in range(len(Adj)):
				for jj in range(len(Adj[ii])):
					if Adj[ii][jj] != 0:
						t_e += 1
						if nodes[ii] == nodes[jj]:
							i_e += 1
						else:
							c_e += 1
			result['total_edges'] = t_e
			result['intra_edges'] = i_e
			result['cross_edges'] = c_e

			result['sparse_total_edges'] = len(sparse)
			s_c_e = 0
			s_i_e = 0
			sparse_nodes = []
			for s in sparse:
				if nodes[s['source']] == nodes[s['target']]:
					s_i_e += 1
				else:
					s_c_e += 1
				sparse_nodes.append(s['source'])
				sparse_nodes.append(s['target'])
			sparse_nodes = list(set(sparse_nodes))
			result['sparse_nodes'] = len(sparse_nodes)
			result['sparse_intra_edges'] = s_i_e
			result['sparse_cross_edges'] = s_c_e
			results.append(result)
	keys = ['groups', 'nodes', 'sparse_nodes', 'total_edges', 'intra_edges', 'cross_edges', 'sparse_total_edges', 'sparse_intra_edges', 'sparse_cross_edges']
	with open(output_file, 'w') as f:
		for result in results:
			for key in keys:
				if key == keys[-1]:
					f.write(str(result[key]) + '\n')
				else:
					f.write(str(result[key]) + '\t')



#ARGUMENT PARSING CODE
data_p = os.path.join(global_paths.data, 'modules', 'reddit_crawler')

description = 'Collects all the results'
arg_vars = {
	'data_path': {'help': 'Path to where data is stored', 'value': data_p},
}
flag_vars = {
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)