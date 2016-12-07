with open('matrix_users_graph.txt', 'r') as f:
	data = f.readlines()

data = [[int(q) for q in x.strip().split('\t')] for x in data]

with open('matrix_users_graph_upper.txt', 'w') as f:
	for ii in range(len(data)):
		for jj in range(len(data[ii])):
			if ii >= jj:
				f.write("0\t")
			else:
				f.write("{}\t".format(data[ii][jj]))
		f.write('\n')