#This module defines the LSR-weighted routine

import copy
import random

#Setup starting probabilities
#
#@input G<Graph>: graph object
#@return starting_prob<list<float>>: list of starting probabilities
#@return total_starting_prob<float>: total starting probabilities
#
def setup_starting_probabilities(G):
	total_starting_prob = 0
	starting_prob = []
	total = 0
	for v in G.V:
		starting_prob.append((G.degree(v)/G.total_degree()) + (G.node_strength(v)/G.total_node_strength()))
		total += starting_prob[-1]
	for v in G.V:
		starting_prob[v] /= total
	for v in G.V:
		starting_prob[v] = (1/(G.N-1)*(1-starting_prob[v]))
	total_starting_prob = starting_prob[0]
	for ii in range(1, len(starting_prob)):
		total_starting_prob += starting_prob[ii]
		starting_prob[ii] += starting_prob[ii-1]
	return starting_prob, total_starting_prob

#Obtain the starting node
#
#@input starting_prob<list<float>>: list of starting probabilities
#@input total_starting_prob<float>: total starting probabilities
#@return starting_node<int>: starting vertex
#
def get_starting_node(starting_prob, total_starting_prob):
	rnd = random.random()*total_starting_prob

	if rnd <= starting_prob[0]:
		return 0
	for ii in range(1, len(starting_prob)):
		if starting_prob[ii-1] < rnd and starting_prob[ii] >= rnd:
			return ii
	return -1

#LSR-WEIGHTED creates a measurement matrix satisfying the constraints for Sparse network analysis
#
#@input G<Graph>: Graph object
#@input m<int>: number of measurements
#@input s<int>: length of measurements
#@return A<list<list>>: Matrix
#
def LSR_WEIGHTED(G, m, s):
	A = []
	P_t = []


	starting_prob, total_starting_prob = setup_starting_probabilities(G)


	for ii in range(m):
		print("Running measurement {} of {}...".format(ii+1, m))
		A_i = []
		for jj in range(G.E_length):
			A_i.append(0)

		v_c = get_starting_node(starting_prob, total_starting_prob)
		input(v_c)

		node_path = [v_c]

		for jj in range(s):
			print("Measurement length {} of {}...".format(jj+1, s))
			if len(G.get_neighbor_list(v_c)) > 0:
				P_t_row = []
				for u in G.V:
					if u != v_c:
						P_t_row.append(G.s_3(v_c, u)/G.total_s_3(v_c))
				v_n = P_t_row.index(max(P_t_row))
				G.remove_neighbor(v_c, v_n)
				node_path.append(v_n)
				edge_number = G.find_edge(v_c, v_n)
				if edge_number == -1:
					input("ERROR edge_number = -1")
				A_i[edge_number] = 1
			else:
				if len(node_path) > 0:
					v_n = node_path.pop()
				else:
					break
			v_c = v_n
		A.append(copy.deepcopy(A_i))
	return A


