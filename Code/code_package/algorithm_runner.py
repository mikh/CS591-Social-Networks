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


#runs the script
def _run(data_base, name, matlab_path):
	input_path = os.path.join(data_base, 'inputs', name + '.txt')
	output_path = os.path.join(data_base, 'raw_results', name + '.txt')
	if name == '' or not path_lib.file_exists(input_path) or matlab_path == '' or not path_lib.file_exists(matlab_path):
		print("Please specify input file")
		sys.exit(-1)
	matlab_code_base = os.path.join(global_paths.base, 'matlab')
	matlab_code_config = os.path.join(matlab_code_base, 'config.txt')
	matlab_code_script = os.path.join(matlab_code_base, 'run_algorithm.m')

	with open(matlab_code_config, 'w') as f:
		f.write('{}\n'.format(input_path))
		f.write('{}\n'.format(output_path))

	command = '"{}" -nodisplay -nosplash -nodesktop -r "run(\'{}\');"'.format(matlab_path, matlab_code_script)
	print(command)
	os.system(command)


#ARGUMENT PARSING CODE
data_base = os.path.join(global_paths.data, 'modules', 'reddit_crawler')
name = ''


description='Script that runs the algorithm'

arg_vars = {
	'data_base': {'help': 'base path to data', 'value':data_base},
	'name': {'help': 'name of graph', 'value': name},
	'matlab_path': {'help': 'path to matlab exe', 'value': ''}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)