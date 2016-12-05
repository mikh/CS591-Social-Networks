#Objects and functions used for graph analysis

import copy

#Graph class 
class Graph():

	#Builds the graph
	#
	#@input self<Graph>: Object self-reference
	#@input Adj<list<list>>: weighted adjacency matrix
	#
	def __init__(self, Adj):
		self.N = len(Adj)
		self.Adj = []
		self.V = []
		self.E = []
		self.Nbr = []
		u_list = {}
		for ii in range(self.N):
			self.V.append(ii)
			row = []
			nbrs = []
			for jj in range(self.N):
				if Adj[ii][jj] != 0:
					row.append(1)
					if not ii in u_list or not jj in u_list[ii]:
						self.E.append([min(ii, jj), max(ii, jj)])
						nbrs.append(jj)
						if not ii in u_list:
							u_list[ii] = []
						u_list[ii].append(jj)
				else:
					row.append(0)
			self.Adj.append(copy.deepcopy(row))
			self.Nbr.append(copy.deepcopy(nbrs))
		self.w = copy.deepcopy(Adj)

		self.E_length = len(self.E)

	#Calculates the score of a vertex
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: vertex 
	#@return score<float>: score value
	#
	def score(G, v):
		term_1 = G.degree(v) / (2 * G.E_length)
		ns_v = G.node_strength(v)
		term_2_d = 0
		for v_i in G.V:
			if v_i != v:
				term_2_d += G.node_strength(v_i)
		term_2 = ns_v / term_2_d
		return term_1 + term_2

	#Calculates the degree of a vertex
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: vertex
	#@return d<int>: degree of vertex
	#
	def degree(G, v):
		d = 0
		for u in range(len(G.Adj[v])):
			d += G.Adj[v][u]
		return d

	#Calculates the node strength of a vertex
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: vertex
	#@return ns<int>: node strength of vertex
	#
	def node_strength(G, v):
		ns = 0
		for u in range(len(G.w[v])):
			ns += G.w[v][u]
		return ns

	#Gets the neighbor list of a vertex
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: vertex
	#@return nbr<list>: list of neighbors
	#
	def get_neighbor_list(G, v):
		return G.Nbr[v]

	#Calculates the score_1 function for a vertex and a neighbor
	#
	#@input G<Graph>: Object self-reference
	#@input v_c<int>: base vertex
	#@input u<int>: neighbor vertex
	#@return score_1<float>: score_1 calculation
	#
	def s_1(G, v_c, u):
		return 1/G.degree(v_c) * min(1, G.degree(v_c)/G.degree(u))

	#Calculates the score_2 function for a vertex and a neighbor
	#
	#@input G<Graph>: Object self-reference
	#@input v_c<int>: base vertex
	#@input u<int>: neighbor vertex
	#@return score_2<float>: score_2 calculation
	#
	def s_2(G, v_c, u):
		nu = G.node_strength(v_c)
		de = G.w[v_c][u] * min(1, G.node_strength(v_c)/G.node_strength(u))
		return nu/de

	#Calculates the score = score_1+score_2 function
	#
	#@input G<Graph>: Object self-reference
	#@input v_c<int>: base vertex
	#@input u<int>: neighbor vertex
	#@return score_3<float>: score_3 calculation
	#
	def s_3(G, v_c, u):
		return G.s_1(v_c, u) * G.s_2(v_c, u)

	#Calculates the s_3 for all u
	#
	#@input G<Graph>: Object self-reference
	#@input v_c<int>: base vertex
	#@return tot<float>: total s_3 calculation
	#
	def total_s_3(G, v_c):
		tot = 0
		for u in G.V:
			if u != v_c:
				tot += s_3(v_c, u)
		return tot

	#Removes a neighbor from the neighbor lists
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: base vertex
	#@input u<int>: other vertex
	#
	def remove_neighbor(G, v, u):
		del G.Nbr[v][G.Nbr[v].index(u)]
		del G.Nbr[u][G.Nbr[u].index(v)]
		G.Adj[v][u] = 0
		G.Adj[u][v] = 0
		G.w[v][u] = 0
		G.w[u][v] = 0

	#Finds the edge given two vertices
	#
	#@input G<Graph>: Object self-reference
	#@input v<int>: vertex one
	#@input u<int>: vertex two
	#@return e_index<int>: index of edge in edge list
	#
	def find_edge(G, v, u):
		edge = [min(u, v), max(v, u)]
		for ii in range(len(G.E)):
			if G.E[ii][0] == edge[0] and G.E[ii][1] == edge[1]:
				return ii
		return -1


