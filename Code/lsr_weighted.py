#This module defines the LSR-weighted routine

import copy

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

	for ii in range(m):
		print("Running measurement {} of {}...".format(ii+1, m))
		A_i = []
		for jj in range(G.E_length):
			A_i.append(0)

		#first node selection
		node_scores = [G.score(v) for v in G.V]
		tot_score = sum(node_scores)
		P_f = []

		for v in G.V:
			P_f.append(1/(G.N-1)*(1-G.score(v)/tot_score))

		#select first node relative to P_f(v) as current node
		v_c = P_f.index(max(P_f))
		node_path = [v_c]

		for jj in range(s):
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


