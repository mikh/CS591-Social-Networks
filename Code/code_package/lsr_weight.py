#Script that runs the algorithm

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



class Graph():
	edges = []
	num_nodes = 0
	num_edges = 0

	def __init__(self, Adj):
		self.Adj = copy.deepcopy(Adj)
		self.num_nodes = len(Adj)
		for x in range(1, len(Adj)):
			for y in range(x+1, len(Adj)):
				if Adj[x][y] != 0:
					self.edges.append([x,y])
					self.num_edges += 1		

	def neighbors(self, v):
		ne = []
		for ii in range(self.num_nodes):
			if self.Adj[v][ii] != 0:
				ne.append(ii)
			if self.Adj[ii][v] != 0:
				ne.append(ii)
		ne = list(set(ne))
		return ne

	def degree(self, v):
		return len(self.neighbors(v))

	def integrity(self):
		num_nodes = self.num_nodes
		if len(self.Adj) != num_nodes:
			return False
		for row in self.Adj:
			if len(row) != num_nodes:
				return False
		return True

	def find_edge(self, u, v):
		for ii in range(len(self.edges)):
			edge = self.edges[ii]
			if edge[0] == min(u,v) and edge[1] == max(u,v):
				return ii
		return -1

def neighbor_weight(v, A):
	su = 0
	for ii in range(len(A)):
		su += A[ii][v]
		su += A[v][ii]
	return su

def score_of_vertex(v, G, sumNeighbor):
	deg = G.degree(v)
	score = deg/(G.num_edges) + sumNeighbor[v]/sum(sumNeighbor)
	return score

#Loads the adjacency matrix
def load_matrix(path):
	A = []
	with open(path, 'r') as f:
		data = f.readlines()
	for line in data:
		A.append([float(x.strip()) for x in line.strip().split(' ')])
	return A

#creates a matrix with a default value
def create_matrix(rows, columns, default_value):
	if rows == 1 or columns == 1:
		return [default_value for c in range(max(rows, columns))]
	return [[default_value for c in range(columns)] for r in range(rows)]

#counts the edges
def count_edges(matrix):
	num_edges = 0
	for x in matrix:
		for y in x:
			if y != 0:
				num_edges += 1
	return num_edges

def Pf_of_vertex(G, A, nodeID):
	if len(G.neighbors(nodeID)) == 0:
		return 0
	N = G.num_nodes
	sumNeighbor = create_matrix(1,N,0)
	for ii in range(N):
		M = G.neighbors(ii)
		for jj in range(len(M)):
			sumNeighbor[ii] += A[ii][M[jj]]
	su = create_matrix(1, N, 0)
	for ii in range(N):
		su[ii] = score_of_vertex(ii, G, sumNeighbor)
	S = sum(su)
	score = su[nodeID]

	return (1-(score/S)) * (1/(N-1))


#runs the script
def _run(data_base, name):
	input_path = os.path.join(data_base, 'inputs', name + '.txt')
	if name == '' or not path_lib.file_exists(input_path):
		print("Please specify input file")
		sys.exit(-1)

	A_original = load_matrix(input_path)
	A = copy.deepcopy(A_original)
	G_original = Graph(A)
	G = copy.deepcopy(G_original)

	N = len(A)
	num_E = count_edges(A)
	m = int(num_E/15)
	s = m
	print("Number of nodes: {}".format(N))
	print("Number of edges: {}".format(num_E))
	print("m: {}".format(m))
	print("s: {}".format(s))

	B = create_matrix(m, num_E, 0)
	y = create_matrix(1, m, 0)

	iteration = 0
	iteration_total = m*s
	for ii in range(m):
		
		G = Graph(A)

		Pf = create_matrix(1, N, 0)

		for jj in range(N):
			Pf[jj] = Pf_of_vertex(G, A, jj)

		maxx = max(Pf)
		Vc = Pf.index(maxx)

		B_edge_index = create_matrix(1, s, 0)
		y_sumi = 0
		Uvc = create_matrix(1,2,0)

		for jj in range(s):
			iteration += 1
			console_lib.update_progress_bar(iteration/iteration_total, 'Performing {}...'.format(iteration))

			G = Graph(A)

			M = G.neighbors(Vc)
			Uvc[0] = Vc
			if len(M) != 0:
				scoren = create_matrix(1, len(M), 0)

				for kk in range(len(M)):
					score1 = min(1, len(M)/G.degree(M[kk]))/len(M)
					score2 = neighbor_weight(Vc, A)
					denom = A[Vc][M[kk]] + A[M[kk]][Vc]
					denom *= min(1, neighbor_weight(Vc, A)/neighbor_weight(M[kk], A))
					score2 /= denom
					scoren[kk] = score1*score2

				hg = sum(scoren)
				Pt = [x/hg for x in scoren]
				maxx = max(Pt)
				Vn_id = Pt.index(maxx)

				Vn = M[Vn_id]

				ei = G.find_edge(Vc, Vn)
				if ei == -1:
					print('FATAL: no edge in ({}, {})'.format(Vc, Vn))
					break

				B_edge_index[jj] = ei
				B[ii][ei] = 1
				y_sumi += G.Adj[min(Vc,Vn)][max(Vc, Vn)]

				A[Vc][Vn] = 0
				A[Vn][Vc] = 0
				Uvc[1] = Vn
			else:
				Vn = Uvc[0]
			Vc = Vn
		y[ii] = y_sumi
		





	console_lib.update_progress_bar(1, 'Done', end=True)




#ARGUMENT PARSING CODE
data_base = os.path.join(global_paths.data, 'modules', 'reddit_crawler')
name = ''


description='Script that runs the algorithm'

arg_vars = {
	'data_base': {'help': 'base path to data', 'value':data_base},
	'name': {'help': 'name of graph', 'value': name}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)