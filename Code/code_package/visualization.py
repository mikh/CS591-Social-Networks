#Loads graph data and creates a visualization of the data

import os
import json
import copy
import math
import random

from lib import const_lib
from lib import path_lib
from lib import arg_lib
from lib import console_lib
from lib.log_lib import *

import plotly_visualization

module_name = 'visualization'

const = const_lib.load_module_const(module_name)
global_paths = const_lib.load_global_paths()

#Loads a matrix file into an array
#
#@input file_path<string>: path to matrix file
#@return matrix<list<list<float>>>: matrix data
#@return entries<int>: number of matrix entries
#
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

#Setup grouping based on number of edges
#
#@input nodes<list<dict>>: list of nodes
#@return nodes<list<dict>>: list of nodes with groups
#
def setup_grouping_edges(nodes):
	edge_numbers = {}
	for node in nodes:
		n = node['number_of_edges']
		if not n in edge_numbers:
			edge_numbers[n] = 0
		edge_numbers[n] += 1

	e_n_keys = sorted(list(edge_numbers.keys()))
	N = len(nodes)
	P = int(N/const.number_of_groups)
	C = 0
	G = 1
	groupings = {}
	for key in e_n_keys:
		groupings[key] = G
		C += edge_numbers[key]
		if C > P and G < const.number_of_groups:
			G += 1
			C = 0
	for ii in range(0, len(nodes)):
		nodes[ii]['group'] = groupings[nodes[ii]['number_of_edges']]

	return nodes

#Gets list of node neighbors
#
#@input w<list<list<float>>>: weight list
#@input v<int>: vertex
#@return nbr<list<int>>: list of neighbors
#
def _get_neighbors(w, v):
	nbr = []
	for ii in range(len(w[v])):
		if w[v][ii] != 0:
			nbr.append(ii)
	return nbr

#identifies connected nodes
#
#@input w<list<list<float>>>: weight list
#@return n<list<list<int>>: list of connected nodes
#
def _get_connected_nodes(w):
	n = []
	V = len(w)
	non_scanned_nodes = [ii for ii in range(V)]

	while len(non_scanned_nodes) > 0:
		v = non_scanned_nodes[0]
		del non_scanned_nodes[0]
		nbrs = _get_neighbors(w, v)
		found = False

		for ii in range(len(n)):
			if v in n[ii]:
				found = True
			if not found:
				for nbr in nbrs:
					if nbr in n[ii]:
						found = True
						break

			if found:
				n[ii].append(v)
				n[ii].extend(nbrs)
				n[ii] = list(set(n[ii]))
				break
		if not found:
			new_row = [v]
			new_row.extend(nbrs)
			n.append(new_row)
		#print("v = {}".format(v))
		#print("nbrs = [{}]".format(", ".join([str(x) for x in nbrs])))
		#print("\n".join(["[{}]".format(", ".join([str(f) for f in x])) for x in n]))
		#input("*"*20)
	old_len = 0
	while(len(n) != old_len):
		ii = -1
		jj = -1
		old_len = len(n)
		for ii in range(len(n)):
			for jj in range(ii+1, len(n)):
				match = False
				for q in n[ii]:
					if q in n[jj]:
						print("{} found".format(q))
						match = True
						break
				if match:
					break
			if match:
				break
		if ii != -1 and jj != -1 and ii != jj:
			print("Merge {} and {}".format(ii, jj))
			print("n[ii] = [{}]".format(", ".join([str(x) for x in n[ii]])))
			print("n[jj] = [{}]".format(", ".join([str(x) for x in n[jj]])))
			print("*"*20)
			n[ii].extend(n[jj])
			n[ii] = list(set(n[ii]))
			del n[jj]

	print(len(n))
	print("\n".join(["[{}]".format(", ".join([str(f) for f in x])) for x in n]))

	input('pause')

#Runs the Floyd Warshall all-pair shortest paths algorithm
#
#@input w<List<list<float>>>: weight list
#@input V<int>: number of nodes
#@return dist<list<list<float>>>: matrix of distances
#
def _Floyd_Warshall(w, V):
	max_value = -1
	for ii in range(V):
		for jj in range(V):
			if w[ii][jj] != 0 and max_value < w[ii][jj]:
				max_value = w[ii][jj]
	for ii in range(V):
		for jj in range(V):
			if w[ii][jj] != 0:
				w[ii][jj] = max_value - w[ii][jj]
	dist = []
	for ii in range(V):
		row = []
		for jj in range(V):
			row.append(math.inf)
		dist.append(copy.deepcopy(row))
	for u in range(V):
		for v in range(V):
			if u == v:
				dist[v][v] = 0
			else:
				if w[u][v] == 0:
					dist[u][v] = math.inf
				else:
					dist[u][v] = w[u][v]
	iteration = 0
	for k in range(V):
		for i in range(V):
			for j in range(V):
				iteration += 1
				if iteration % 10000 == 0:
					console_lib.update_progress_bar(iteration/(V*V*V), "Performing Floyd-Warshall analysis iteration={} k={}, i={}, j={}...".format(iteration, k,i,j))
				if dist[min(i, j)][max(i, j)] > dist[min(i, k)][max(i, k)] + dist[min(j, k)][max(k, j)]:
					dist[min(i, j)][max(i, j)] = dist[min(i, k)][max(i, k)] + dist[min(j, k)][max(k, j)]
	console_lib.update_progress_bar(1, "Floyd-Warshall complete.", end=True)
	return dist

#Checks if the results have converged
#
#@input old_group_centers<list<int>>: old group centers
#@input new_group_centers<list<int>>: new group centers
#@input iterations<int>: number of iterations run
#@return converged<boolean>: returns True if converged
#
def _check_convergence(old_group_centers, new_group_centers, iterations):
	if iterations == 0:
		return False
	if const.convergence_iterations <= iterations:
		return True
	for ii in range(len(old_group_centers)):
		if old_group_centers[ii] != new_group_centers[ii]:
			return False
	return True

#Creates groupings based on k-means clustering
#
#@input matrix<list<list<float>>>: matrix data
#@input nodes<list<dict>>: list of nodes
#@return nodes<list<dict>>: list of nodes with groups
#@return group<dict<list<int>>>: list of groupings
#
def _setup_grouping_kmeans(matrix, nodes):
	print("Running K-Means clustering...")
	#_get_connected_nodes(matrix)
	V = len(nodes)
	dist = _Floyd_Warshall(matrix, len(matrix))

	#choose start nodes
	group_centers = []
	for ii in range(const.number_of_groups):
		r = -1
		while r == -1 or r in group_centers:
			r = random.randint(0, len(nodes)-1)
		group_centers.append(r)

	iterations = 0
	new_group_centers = []
	while not _check_convergence(group_centers, new_group_centers, iterations):
		iterations += 1
		console_lib.update_progress_bar(iterations/const.convergence_iterations, "K-Means iteration {}".format(iterations))
		groups = {}
		for g in range(const.number_of_groups):
			groups[g] = []
		for v in range(V):
			distances = [dist[min(v, x)][max(v, x)] for x in group_centers]
			group = distances.index(min(distances))
			groups[group].append(v)

		new_group_centers = []
		for group in range(const.number_of_groups):
			g_nodes = groups[group]
			N = len(g_nodes)
			avg_d = []
			for g in g_nodes:
				distances = [dist[min(g, x)][max(g, x)] for x in g_nodes]
				avg_d.append(sum(distances)/N)
			min_i = avg_d.index(min(avg_d))
			new_group_centers.append(g_nodes[min_i])
	console_lib.update_progress_bar(1, "K-Means done.", end=True)

	for group in groups:
		for node in groups[group]:
			nodes[node]['group'] = group
	return nodes, groups

#Processes the matrix into a series of nodes and edges
#
#@input matrix<list<list<float>>>: matrix data
#@input labels<list<string>>: node labels
#@return nodes<list<dict>>: list of nodes
#@return edges<list<dict>>: list of edges
#@return groups<dict<list<int>>>: dictionary of groups
#
def _process_matrix(matrix, labels=None):
	nodes = []
	for ii in range(0, len(matrix)):
		node = {'id': ii}
		if labels != None:
			node['name'] = labels[ii]

		connecting_nodes = []
		for jj in range(0, len(matrix[ii])):
			if matrix[ii][jj] != 0:
				connecting_nodes.append(jj)
			if matrix[jj][ii] != 0:
				connecting_nodes.append(jj)
		connecting_nodes = list(set(connecting_nodes))
		node['connecting_nodes'] = connecting_nodes
		n_o_e = len(connecting_nodes)
		node['number_of_edges'] = n_o_e

		nodes.append(node)
	edges = []
	for ii in range(0, len(matrix)):
		for jj in range(0, len(matrix[ii])):
			if matrix[ii][jj] != 0:
				edge = {'source':ii, 'target': jj, 'value': matrix[ii][jj]}
				edges.append(edge)

	#nodes = setup_grouping_edges(nodes)
	nodes, groups = _setup_grouping_kmeans(matrix, nodes)
	#input('pause')

	return nodes, edges, groups

#Runs the script
#
#@input log_path<string>: path to log file to store results of script run
#@input data_path<string>: path to data folder for module
#@input matrix_file<string>: filename of matrix to load
#@input label_file<string>: filename of label file
#@input plotly<boolean>: use plotly for visualization
#@input iris<boolean>: use iris for visualization
#
def _run(log_path, data_path, matrix_file, label_file, plotly, iris):
	log_file = define_log_file(log_path, log_path=log_path)
	script_timer = log_start(log_file)

	path_lib.create_path(data_path)

	log(log_file, 'Loading matrix file...')
	matrix, entries = _load_matrix_data(os.path.join(data_path, matrix_file))
	log(log_file, 'Matrix loaded. Contains {} entries.'.format(entries))

	labels = None
	if label_file != None:
		log(log_file, 'Loading label file...')
		with open(os.path.join(data_path, label_file), 'r') as f:
			labels = f.readlines()
		labels = [x.strip() for x in labels]
		log(log_file, 'Labels loaded.')

	log(log_file, 'Process matrix file...')
	nodes, edges, groups = _process_matrix(matrix, labels=labels)
	log(log_file, 'Matrix Processed. {} nodes and {} edges loaded.'.format(len(nodes), len(edges)))

	if plotly:
		log(log_file, 'Visualize with plotly...')
		plotly_visualization.visualize(nodes, edges, groups)
		log(log_file, 'Visualization ready.')
	elif iris:
		log(log_file, 'Visualize with IRIS...')
		iris_visualization.visualize(nodes, edges, log_file)
		log(log_file, 'Visualization ready.')
	else:
		log(log_file, 'No visualization selected.')

	log_end(log_file, timer=script_timer)

#ARGUMENT PARSING CODE
log_p = os.path.join(global_paths.logs, 'modules', module_name, module_name+'.log')
data_p = os.path.join(global_paths.data, 'modules', module_name)
matrix_p = 'matrix_users_graph.txt'
label_p = None

description = 'Loads graph data and creates a visualization of the data'
arg_vars = {
	'log_path': {'help': 'Path to where log data is stored', 'value': log_p},
	'data_path': {'help': 'Path to where data is stored', 'value': data_p},
	'matrix_file': {'help': 'Filename of matrix data to visualizze', 'value': matrix_p},
	'label_file': {'help': 'Filename of node labels', 'value': label_p}
}
flag_vars = {
	"plotly" : {"help": "Visualize using plotly", "value": True},
	"iris": {"help": "Visualize using IRIS", "value": False},
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)
