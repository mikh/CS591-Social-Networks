#Module to perform social network analysis

import graph_objects
import lsr_weighted

#Loads the data from files into a weighted adjacency matrix
#
#@input path<string>: path to data
#@return Adj<list<list>>: weighted adjacency matrix
#
def load_data(path):
	print("Loading data.")
	with open(path, 'r') as f:
		data = f.readlines()
	Adj = []
	for line in data:
		line = line.strip().split('\t')
		row = [float(x.strip()) for x in line]
		Adj.append(row)
	return Adj

#Saves the data
#
#@input path<string>: path to data
#@input A<list<list>>: data matrix
#
def save_data(path, A):
	with open(path, 'w') as f:
		for ii in range(len(A)):
			for jj in range(len(A[ii])):
				f.write("{}\t".format(A[ii][jj]))
			f.write('\n')

#Integrity checks weighted adjacency matrix dimensions
#
#@input Adj<list<list>>: weighted adjacency matrix
#@return pass<boolean>: returns True if the matrix passes the integrity check
#
def integrity_check(Adj):
	print("Performing integrity check.")
	N = len(Adj)
	for row in Adj:
		if len(row) != N:
			print("Integrity Check Failed!")
			return False
	print("Integrity Check Passed. Matrix is [{}x{}]".format(N, N))
	return True





path = 	"D:\\Digital_Library\\data\\Documents\\Class\\CS_592_Compressive_Sensing\\Project\\Data\\Social Network Data\\Basic\\matrix_users_graph.txt"	
path_save = "D:\\Digital_Library\\data\\Documents\\Class\\CS_592_Compressive_Sensing\\Project\\Data\\Social Network Data\\Basic\\A.txt"	

Adj = load_data(path)
if integrity_check(Adj):
	G = graph_objects.Graph(Adj)

	m = int(G.N*.2)
	s = int(G.E_length/5)

	A = lsr_weighted.LSR_WEIGHTED(G, m, s)
	save_data(path_save, A)


