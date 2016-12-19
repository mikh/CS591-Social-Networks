#Script that creates an Adjacency matrix

import os
import sys
import random
import json

from lib import const_lib
from lib import path_lib
from lib import arg_lib
from lib import console_lib

global_paths = const_lib.load_global_paths()











#integrates users file
def integrate_users(sub_users, users, subreddits, nodes, same_group_thresh, diff_group_high, diff_group_low, percentage_cross):
	for u in users:
		u = users[u]
		values = []
		for sub in subreddits:
			values.append(u['subreddits'][sub])
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
		users[u]['subreddits'] = new_subreddits
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
def _run(data_base, groups, nodes, name, same_group_thresh, diff_group_high, diff_group_low, percentage_cross):
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



#ARGUMENT PARSING CODE
data_base = os.path.join(global_paths.data, 'modules', 'reddit_crawler')
groups = 0
nodes = 0
name = ''
same_group_thresh=0.7
diff_group_high=0.2
diff_group_low=0.1
percentage_cross=0.1


description='Script that creates an Adjacency matrix'

arg_vars = {
	'data_base': {'help': 'base path to data', 'value':data_base},
	'groups': {'help': 'number of groups to look for', 'value': groups},
	'nodes': {'help': 'number of total nodes', 'value': nodes},
	'name': {'help': 'name of graph', 'value': name},
	'same_group_thresh': {'help': 'Threshold to determine if the same group is accepted', 'value': same_group_thresh},
	'diff_group_high': {'help': 'Upper bound for different group connection', 'value': diff_group_high},
	'diff_group_low': {'help': 'Lower bound for different group connection', 'value': diff_group_low},
	'percentage_cross': {'help': 'Percentage of a group that should have cross links', 'value': percentage_cross}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)

