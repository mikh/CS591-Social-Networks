#Script that creates an Adjacency matrix

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



#determines link quality between 2 nodes (larger is stronger)
def get_link_quality(u, v):
	link = 0
	for sub in u['subreddits']:
		if sub in v['subreddits']:
			link += min(u['subreddits'][sub], v['subreddits'][sub])
	return link

#links the same_group nodes
def link_same_group_nodes(l, num_connections):
	for ii in range(len(l)):
		u = l[ii]
		total = 0
		for s in u['subreddits']:
			total += u['subreddits'][s]
		for s in u['subreddits']:
			u['subreddits'][s] /= total
		l[ii] = u

	connection_matrix = [[-1 for x in range(len(l))] for y in range(len(l))]
	max_link = 0
	for x in range(0, len(l)):
		for y in range(x+1, len(l)):
			connection_matrix[x][y] = get_link_quality(l[x], l[y])
			if connection_matrix[x][y] > max_link:
				max_link = connection_matrix[x][y]

	for x in range(0, len(l)):
		for y in range(x+1, len(l)):
			connection_matrix[x][y] /= max_link
			connection_matrix[x][y] = 0.3 - (0.2 * connection_matrix[x][y])

	for x in range(len(l)):
		if len(range(x+1, len(l))) > num_connections:
			chosen_nodes = random.sample(range(x+1, len(l)), num_connections)
			for y in range(x+1, len(l)):
				if not y in chosen_nodes:
					connection_matrix[x][y] = -1

	return connection_matrix

def link_cross_group_nodes(sub_users, sub, diff_group_low, diff_group_high):
	local = sub_users[sub]
	for xx in range(len(local)):
		if local[xx]['cross']:
			local[xx]['cross_links'] = []
			cross_node = local[xx]
			cross_subs = []
			for sub in cross_node['link_subreddits']:
				v = cross_node['link_subreddits'][sub]
				if v >= diff_group_low and v <= diff_group_high:
					cross_subs.append(sub)
			for cross_sub in cross_subs:
				cross = sub_users[cross_sub]
				cross_connections = []
				for ii in range(len(cross)):
					cross_connections.append(get_link_quality(cross_node, cross[ii]))
				cross_connections = [x/max(cross_connections) for x in cross_connections]
				cross_connection = random.randint(0, len(cross_connections)-1)
				cross_connection_value = 0.8 + (0.1 * cross_connections[cross_connection])
				local[xx]['cross_links'].append([cross_sub, cross_connection, cross_connection_value])
	sub_users[sub] = local
	return sub_users

#Creates links between nodes
def link_nodes(sub_users, num_connections, nodes, diff_group_low, diff_group_high):
	connection_matrix = [[-1 for x in range(nodes)] for y in range(nodes)]
	next_node = 0
	offsets = {}
	keys = list(sub_users.keys())
	for ii in range(len(keys)):
		offsets[keys[ii]] = next_node
		next_node += len(sub_users[keys[ii]])

	for ii in range(len(keys)):
		sub = keys[ii]
		c_mat = link_same_group_nodes(sub_users[sub], num_connections)
		for x in range(len(c_mat)):
			for y in range(x+1, len(c_mat)):
				connection_matrix[x+offsets[keys[ii]]][y+offsets[keys[ii]]] = c_mat[x][y]
		sub_users = link_cross_group_nodes(sub_users, sub, diff_group_low, diff_group_high)
		for jj in range(len(sub_users[sub])):
			if sub_users[sub][jj]['cross']:
				cross_connections = sub_users[sub][jj]['cross_links']
				src = jj + offsets[keys[ii]]

				for cross in cross_connections:
					dest = offsets[cross[0]] + cross[1]
					connection_matrix[min(src, dest)][max(src, dest)] = cross[2]

	return connection_matrix

#write to matlab file
def write_to_matlab_file(path, c_mat):
	with open(path, 'w') as f:
		def transform(y):
			if y == -1:
				return "0"
			else:
				return "{:.2}".format(y)
		f.write('[')
		f.write("; ".join([", ".join([transform(y) for y in x]) for x in c_mat]))
		f.write('];')


#integrates users file
def integrate_users(sub_users, users, subreddits, nodes, same_group_thresh, diff_group_high, diff_group_low, percentage_cross):
	for u in users:
		u = users[u]
		values = []
		for sub in subreddits:
			values.append(u['link_subreddits'][sub])
		highest = max(values)
		if highest >= same_group_thresh:
			subreddit = subreddits[values.index(highest)]
			u['primary'] = subreddit
			u['cross'] = False
			for v in values:
				if v != highest and (v >= diff_group_low and v <= diff_group_high):
					u['cross'] = True
			sub_users[subreddit].append(u)
	targets_matched = 0
	for sub in sub_users:
		num_nodes = len(sub_users[sub])
		num_cross = len([u for u in sub_users[sub] if u['cross']])

		target_nodes = int(nodes/len(subreddits))
		target_cross = int(target_nodes*percentage_cross)

		if num_cross > target_cross:
			for ii in range(len(sub_users[sub])-1, -1, -1):
				if sub_users[sub][ii]['cross']:
					del sub_users[sub][ii]
					num_cross -= 1
					if num_cross == target_cross:
						break
		num_nodes = len(sub_users[sub])
		if num_nodes > target_nodes:
			for ii in range(len(sub_users[sub])-1, -1, -1):
				if not sub_users[sub][ii]['cross']:
					del sub_users[sub][ii]
					num_nodes -= 1
					if num_nodes == target_nodes:
						break
		if num_nodes == target_nodes and num_cross == target_cross:
			targets_matched += 1

		print('{} u:{} c:{} ({})'.format(sub, num_nodes, num_cross, num_cross/num_nodes))

	return sub_users, targets_matched

#loads user file
def load_file(path, subreddits):
	with open(path, 'r') as f:
		users = json.load(f)
	for u in users:
		total = 0
		for subs in subreddits:
			if subs in users[u]['subreddits']:
				total += users[u]['subreddits'][subs]
		new_subreddits = {}
		for sub in subreddits:
			if not sub in users[u]['subreddits']:
				new_subreddits[sub] = 0
			else:
				new_subreddits[sub] = users[u]['subreddits'][sub]/total
		users[u]['link_subreddits'] = new_subreddits
	return users

#Obtain the highest subreddits in section
def get_top_subreddits(path, num_groups):
	subreddits = {}
	with open(path, 'r') as f:
		users = json.load(f)
	for u in users:
		for sub in users[u]['subreddits']:
			if not sub in subreddits:
				subreddits[sub] = 0
			subreddits[sub] += users[u]['subreddits'][sub]
	sub_list = [[x, subreddits[x]] for x in subreddits.keys()]
	sub_list.sort(key=lambda x:x[1])
	top_subreddits = sub_list[-num_groups:]
	return [x[0] for x in top_subreddits]

#Runs the script
def _run(data_base, groups, nodes, name, same_group_thresh, diff_group_high, diff_group_low, percentage_cross, num_connections):
	groups = int(groups)
	nodes = int(nodes)
	same_group_thresh = float(same_group_thresh)
	diff_group_high = float(diff_group_high)
	diff_group_low = float(diff_group_low)
	percentage_cross = float(percentage_cross)

	if name == '' or groups == 0 or nodes == 0:
		print('Please specify number of nodes, groups, and name of the graph')
		sys.exit(-1)

	target_filename = os.path.join(data_base, 'inputs', name+'.txt')
	src_folder = os.path.join(data_base, 'storage')
	src_files = path_lib.get_all_files_in_directory(src_folder)

	primary = random.randint(0, len(src_files)-1)
	subreddits = get_top_subreddits(os.path.join(src_folder, src_files[primary]), groups)
	sub_users = {}
	for sub in subreddits:
		sub_users[sub] = []
	active_file = primary
	checked_files = []

	while len(checked_files) < len(src_files):
		users = load_file(os.path.join(src_folder, src_files[active_file]), subreddits)
		sub_users, targets_matched = integrate_users(sub_users, users, subreddits, nodes, same_group_thresh, diff_group_high, diff_group_low, percentage_cross)
		if targets_matched == len(subreddits):
			break
		checked_files.append(active_file)
		while active_file in checked_files:
			active_file = random.randint(0, len(src_files)-1)

	connection_matrix = link_nodes(sub_users, num_connections, nodes, diff_group_low, diff_group_high)
	write_to_matlab_file(target_filename, connection_matrix)


#ARGUMENT PARSING CODE
data_base = os.path.join(global_paths.data, 'modules', 'reddit_crawler')
groups = 0
nodes = 0
name = ''
same_group_thresh=0.7
diff_group_high=0.2
diff_group_low=0.1
percentage_cross=0.1
num_connections = 3


description='Script that creates an Adjacency matrix'

arg_vars = {
	'data_base': {'help': 'base path to data', 'value':data_base},
	'groups': {'help': 'number of groups to look for', 'value': groups},
	'nodes': {'help': 'number of total nodes', 'value': nodes},
	'name': {'help': 'name of graph', 'value': name},
	'same_group_thresh': {'help': 'Threshold to determine if the same group is accepted', 'value': same_group_thresh},
	'diff_group_high': {'help': 'Upper bound for different group connection', 'value': diff_group_high},
	'diff_group_low': {'help': 'Lower bound for different group connection', 'value': diff_group_low},
	'percentage_cross': {'help': 'Percentage of a group that should have cross links', 'value': percentage_cross},
	'num_connections': {'help': 'number of intra-group connections', 'value': num_connections}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)

