import igraph as ig
import json
import copy
import random
import urllib.request
import plotly.plotly as py
from plotly.graph_objs import *

py.sign_in('mikh', 'n9r4lux66n')

#Checks if a coordinate is in the coordinate list
#
#@input coord_list<list<list<float>>>: coordinate list
#@input coord<list<float>>: coordinate
#@return coord_exists<boolean>: True if coord exists
#
def in_coords_list(coord_list, coord):
	for c in coord_list:
		coord_exists = True
		for ii in range(len(c)):
			if not c[ii] == coord[ii]:
				coord_exists = False
				break
		if coord_exists:
			return True
	return False

#Multiplies all coordinates in list by a coordinate offset
#
#@input coord_list<list<list<float>>>: coordinate list
#@input coord<list<float>>: multiple coord
#@return coord_list<List<list<float>>>: coordinate list after multplication
#
def multiply_coords(coord_list, coord):
	if isinstance(coord_list, list):
		for ii in range(len(coord_list)):
			for jj in range(len(coord_list[ii])):
				coord_list[ii][jj] *= coord[jj]
	elif isinstance(coord_list, dict):
		for key in coord_list:
			for jj in range(len(coord_list[key])):
				coord_list[key][jj] *= coord[jj]
	return coord_list

#Adds all coordinates in list by a coordinate offset
#
#@input coord_list<list<list<float>>>: coordinate list
#@input coord<list<float>>: add coord
#@return coord_list<List<list<float>>>: coordinate list after addition
#
def add_coords(coord_list, coord):
	if isinstance(coord_list, list):
		for ii in range(len(coord_list)):
			for jj in range(len(coord_list[ii])):
				coord_list[ii][jj] += coord[jj]
	elif isinstance(coord_list, dict):
		for key in coord_list:
			for jj in range(len(coord_list[key])):
				coord_list[key][jj] += coord[jj]
	return coord_list

#Gets the max distance for a coord list
#
#@input coord_list<list<list<float>>>: coordinate list
#@return dist<list<float>>: list of distances
#
def max_distance(coord_list):
	if isinstance(coord_list, list):
		dist = [[0,0] for x in range(len(coord_list[0]))]
		for c in coord_list:
			for d in range(len(c)):
				dist[d][0] = min(dist[d][0], c[d])
				dist[d][1] = max(dist[d][1], c[d])
	elif isinstance(coord_list, dict):
		dist = [[0,0] for x in range(len(coord_list[list(coord_list.keys())[0]]))]
		for key in coord_list:
			for d in range(len(coord_list[key])):
				dist[d][0] = min(dist[d][0], coord_list[key][d])
				dist[d][1] = max(dist[d][1], coord_list[key][d])
	return [abs(x[1] - x[0]) for x in dist]

#Generates the coordinate ball
#
#@input nodes<list<int>>: list of vertex numbers
#@return coord_map<dict<list<int>>>: coordinate mapping
#
def generate_coordinate_ball(nodes):
	coord_list = []
	total_coord_list = []
	new_coord_list = []
	coord_map = {}
	if len(nodes) == 0:
		return None
	coord_list.append([0,0,0])
	total_coord_list.append([0,0,0])
	coord_map[nodes[0]] = [0,0,0]
	ii = 0
	while ii < len(nodes):
		node = nodes[ii]
		found = False

		for c in coord_list:
			for x in range(-1, 2):
				for y in range(-1, 2):
					for z in range(-1, 2):
						nc = copy.deepcopy(c)
						nc[0] += x
						nc[1] += y
						nc[2] += z
						if not in_coords_list(total_coord_list, nc):
							coord_map[node] = nc
							new_coord_list.append(nc)
							total_coord_list.append(nc)
							ii += 1
							found = True
							break
					if found:
						break
				if found:
					break
			if found:
				break

		if not found:
			coord_list = copy.deepcopy(new_coord_list)
			new_coord_list = []
	return coord_map

#Generates a coordinate ball based on base_coords
#
#@input nodes<list<int>>: list of vertex numbers
#@input base_coords<list<list<float>>>: base coordinates
#@return coord_map<dict<list<int>>>: coordinate mapping
#
def generate_coordinate_ball_base_coords(nodes, base_coords):
	coord_map = {}
	ii = 0
	for node in nodes:
		coord_map[node] = base_coords[ii]
		ii += 1
	return coord_map

#Determines graph coordinates for group visualization
#
#@input nodes<list<dict>>: list of nodes
#@input groups<dict<list<int>>>: dictionary of groups
#@input base_coords<list<list<float>>>: base coordinates
#@return nodes<list<dict>>: list of nodes with coordinates
#
def create_coordinates(nodes, groups, base_coords):
	X_ranges = [min([base_coords[k][0] for k in range(len(base_coords))]), max([base_coords[k][0] for k in range(len(base_coords))])]
	Y_ranges = [min([base_coords[k][1] for k in range(len(base_coords))]), max([base_coords[k][1] for k in range(len(base_coords))])]
	Z_ranges = [min([base_coords[k][2] for k in range(len(base_coords))]), max([base_coords[k][2] for k in range(len(base_coords))])]
	offset = [X_ranges[1] - X_ranges[0], Y_ranges[1] - Y_ranges[0], Z_ranges[1] - Z_ranges[0]]
	base_coords = add_coords(base_coords, offset)

	group_sizes = [len(groups[group]) for group in range(len(groups.keys()))]
	group_sizes = [[ii, group_sizes[ii]] for ii in range(len(group_sizes))]
	group_sizes.sort(key=lambda x: x[1])
	group_vertices = [x[0] for x in group_sizes]
	group_vertices_map = generate_coordinate_ball(group_vertices)

	group_coords = {}
	dist_length = 0
	for group in groups:
		#group_coords[group] = multiply_coords(generate_coordinate_ball(groups[group]), [0.5, 0.5, 0.5])
		group_coords[group] = generate_coordinate_ball_base_coords(groups[group], base_coords)
		if max(max_distance(group_coords[group])) > dist_length:
			dist_length = max(max_distance(group_coords[group]))
	for group in group_vertices_map:
		d = max(max_distance(group_coords[group]))/2
		group_vertices_map[group] = multiply_coords([group_vertices_map[group]], [d, d, d])
		group_coords[group] = add_coords(group_coords[group], group_vertices_map[group][0])

	for group in group_coords:
		for v in group_coords[group]:
			nodes[v]['coords'] = group_coords[group][v]

	return nodes


#Runs plotly visualization given a list of nodes and a list of edges
#
#@input nodes<list<dict>>: list of nodes
#@input edges<list<dict>>: list of edges
#@input groups<dict<list<int>>>: dictionary of groups
#@input directed<boolean>: indicates if graph should be directed
#@input title<string>: Title of graph
#@input text<string>: description of graph
#@input filename<string>: web name of graph
#@input hard_edges<list<dict>>: edges that should be high weight
#
def visualize(nodes, edges, groups, directed=False, title='Graph', text='Text', filename='Graph', hard_edges=None):
	print("Running visualization protocol...")

	if hard_edges == None:
		hard_edges = []
		for ii in range(30):
			hard_edges.append(edges[random.randint(0, len(edges)-1)])

	N = len(nodes)
	L = len(edges)

	print("Setting up graph...")
	Edges = [(edges[k]['source'], edges[k]['target']) for k in range(L)]
	Hard_Edges = [(hard_edges[k]['source'], hard_edges[k]['target']) for k in range(len(hard_edges))]
	G = ig.Graph(Edges, directed=directed)

	labels = []
	group = []
	for node in nodes:
		if 'name' in node:
			labels.append(node['name'])
		else:
			labels.append(str(node['id']))
		if 'group' in node:
			group.append(node['group'])
		else:
			group.append(1)

	print("Creating coordinates....")
	layt = G.layout('kk', dim=3)
	base_coords = [[layt[k][0], layt[k][1], layt[k][2]] for k in range(len(layt))]

	nodes = create_coordinates(nodes, groups, base_coords)

	#layt = G.layout('grid_3d', dim=3)
	#Xn = [layt[k][0] for k in range(N)] #x-coords of nodes
	#Yn = [layt[k][1] for k in range(N)] #y-coords
	#Zn = [layt[k][2] for k in range(N)] #z-coords
	Xn = [nodes[k]['coords'][0] for k in range(N)]
	Yn = [nodes[k]['coords'][1] for k in range(N)]
	Zn = [nodes[k]['coords'][2] for k in range(N)]
	Xe = []
	Ye = []
	Ze = []

	print("Creating edges...")
	for e in Edges:
		#Xe += [layt[e[0]][0], layt[e[1]][0], None]	
		#Ye += [layt[e[0]][1], layt[e[1]][1], None]	
		#Ze += [layt[e[0]][2], layt[e[1]][2], None]	
		#print(e)
		#print(layt[e[0]][0])
		#print(layt[e[1]][0])
		#input('')
		Xe += [nodes[e[0]]['coords'][0], nodes[e[1]]['coords'][0], None]
		Ye += [nodes[e[0]]['coords'][1], nodes[e[1]]['coords'][1], None]
		Ze += [nodes[e[0]]['coords'][2], nodes[e[1]]['coords'][2], None]

	Xe_hard = []
	Ye_hard = []
	Ze_hard = []

	for e in Hard_Edges:
		Xe_hard += [nodes[e[0]]['coords'][0], nodes[e[1]]['coords'][0], None]
		Ye_hard += [nodes[e[0]]['coords'][1], nodes[e[1]]['coords'][1], None]
		Ze_hard += [nodes[e[0]]['coords'][2], nodes[e[1]]['coords'][2], None]

	print("Building traces...")
	trace1 = Scatter3d(x = Xe, y=Ye, z=Ze, mode='lines', line=Line(color='rgb(125,125,125)', width=1), hoverinfo='none')
	trace3 = Scatter3d(x=Xe_hard, y=Ye_hard, z=Ze_hard, mode='lines', line=Line(color='rgb(255,0,0)', width=10), hoverinfo='none')
	trace2 = Scatter3d(x=Xn, y=Yn, z=Zn, mode='markers', name='actors', marker=Marker(symbol='dot', size=6, color=group, colorscale='Viridis', line=Line(color='rgb(50,50,50)', width=0.5)), text=labels, hoverinfo='text')
	axis = dict(showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False, title='')
	layout = Layout(title=title, width=1000, height=1000, showlegend=False, scene=Scene(xaxis=XAxis(axis), yaxis=YAxis(axis), zaxis=ZAxis(axis)), margin=Margin(t=100), hovermode='closest', annotations=Annotations([Annotation(showarrow=False, text=text, xref='paper', yref='paper', x=0, y=0.1, xanchor='left', yanchor='bottom', font=Font(size=14))]))
	

	data1 = Data([trace2, trace1])
	data2 = Data([trace2, trace1, trace3])
	data3 = Data([trace2, trace3])
	fig1=Figure(data=data1, layout=layout)
	fig2=Figure(data=data2, layout=layout)
	fig3=Figure(data=data3, layout=layout)

	print("Displaying graph...")
	py.plot(fig1, filename=filename)
	input('Display both full and sparse edges')
	py.plot(fig2, filename=filename)
	input('Display only sparse edges')
	py.plot(fig3, filename=filename)


