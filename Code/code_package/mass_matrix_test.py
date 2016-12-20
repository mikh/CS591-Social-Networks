#Script that tests a lot of matrices

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

def _run(group_start, group_end, group_step, nodes_start, nodes_end, nodes_step, cross_start, cross_end, cross_step, nc_start, nc_end, nc_step, create_graphs, run_algorithm):
	if not run_algorithm:
		group_start = int(group_start)
		group_end = int(group_end)
		group_step = int(group_step)
		nodes_start = int(nodes_start)
		nodes_end = int(nodes_end)
		nodes_step = int(nodes_step)
		cross_start = int(float(cross_start)*10)
		cross_end = int(10*float(cross_end))
		cross_step = int(10*float(cross_step))
		nc_start = int(10*float(nc_start))
		nc_end = int(10*float(nc_end))
		nc_step = int(10*float(nc_step))


		for group in range(group_start, group_end + group_step, group_step):
			for nodes in range(nodes_start, nodes_end+nodes_step,nodes_step):
				for cross in range(cross_start, cross_end + cross_step, cross_step):
					for nc in range(nc_start, nc_end + nc_step, nc_step):

						name = 'reddit_g{}_n{}_cro{}_con{}'.format(group, nodes, cross, nc)
						if create_graphs:

							command = '"py\\Scripts\\python matrix_generator.py --set_groups={groups} --set_nodes={nodes} --set_name={name} --set_percentage_cross={cross} --set_num_connections={nc}"'.format(groups=group, nodes=nodes, name=name, cross=cross/10, nc=nc/10)
							print(command)
							os.system(command)
	else:
		input_folder = os.path.join(global_paths.data, 'modules', 'reddit_crawler', 'inputs')
		output_folder = os.path.join(global_paths.data, 'modules', 'reddit_crawler', 'raw_results')

		input_files = path_lib.get_all_files_in_directory(input_folder)
		output_files = path_lib.get_all_files_in_directory(output_folder)
		print(input_files)
		for file in input_files:
			if 'reddit' in file and 'g' in file and 'n' in file and 'cro' in file and 'con' in file:
				if not file in output_files:
					file = path_lib.get_filename_without_extension(file)
					lock_file = os.path.join(global_paths.base, 'matlab', 'lock.txt')
					with open(lock_file, 'w') as f:
						f.write('1')

					locked = True
					command = '"py\\Scripts\\python algorithm_runner.py --set_name={file} --set_matlab_path="{matlab_path}""'.format()
					os.system(command)

					while locked:
						with open(lock_file, 'r') as f:
							data = f.read()
						if(int(data)) == 1:
							time.sleep(20)
						elif int(data) == 0:
							locked = False

#ARGUMENT PARSING CODE
group_start = 3
group_end = 3
group_step = 1
nodes_start = 1000
nodes_end = 2000
nodes_step = 500
cross_start = 0.1
cross_end = 0.1
cross_step = 0.1
nc_start = 0.3
nc_end = 0.9
nc_step = 0.6

description = 'Script that tests a lot of matrices'

arg_vars = {
	'group_start': {'help': '', 'value':group_start},
	'group_end': {'help':'', 'value': group_end},
	'group_step': {'help':'', 'value': group_step},
	'nodes_start': {'help':'', 'value': nodes_start},
	'nodes_end': {'help':'', 'value': nodes_end},
	'nodes_step': {'help':'', 'value': nodes_step},
	'cross_start': {'help':'', 'value': cross_start},
	'cross_end': {'help':'', 'value': cross_end},
	'cross_step': {'help':'', 'value': cross_step},
	'nc_start': {'help':'', 'value': nc_start},
	'nc_end': {'help':'', 'value': nc_end},
	'nc_step': {'help':'', 'value': nc_step}
}

flag_vars = {
	'create_graphs': {'help': 'creates graphs', 'value': False},
	'run_algorithm': {'help': 'runs the algorithm', 'value': False}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)