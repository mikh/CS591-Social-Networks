#Converts raw data output of matlab to visualization ready data

import sys
import os

from lib import arg_lib
from lib import path_lib
from lib import const_lib

global_paths = const_lib.load_global_paths()

#Parse method 1
#
#@input path<string>: path to raw data file
#@return Adj<list<list<int>>>: Adjacency matrix
#@return sparse<list<int>>: list of sparse edges
#
def parse_method1(path):
	with open(path, 'r') as f:
		data = f.readlines()
	Adj = data[0].strip()[1:-3].split(';')
	Adj = [x.strip().split(',') for x in Adj]
	Adj = [[int(y.strip()) for y in x] for x in Adj]
	sparse = [x.strip() for x in data[1:] if x.strip() != '']
	sparse = [x.split(':')[1].strip() for x in sparse]
	sparse = [[int(x.split('<')[0].strip()) -1, int(x.split('>')[1].strip())-1] for x in sparse]
	return Adj, sparse

#Parse method 1
#
#@input path<string>: path to raw data file
#@return Adj<list<list<int>>>: Adjacency matrix
#@return sparse<list<int>>: list of sparse edges
#
def parse_method2(path):
	with open(path, 'r') as f:
		data = f.readlines()
	Adj = []
	for d in data:
		if d.strip() == '];':
			break
		elif d.strip() != '':
			Adj.append(d.strip())
	Adj = Adj[1:]
	Adj = [x[:-1].strip().split('\t') for x in Adj]
	Adj = [[int(y.strip()) for y in x] for x in Adj]

	index = len(Adj)
	sparse = []
	start = False
	for ii in range(index, len(data)):
		if start:
			sparse.append(data[ii].strip())
		elif 'Found' in data[ii]:
			start = True
	sparse = [x.split(':')[1].strip() for x in sparse]
	sparse = [[int(x.split('<')[0].strip()) -1, int(x.split('>')[1].strip())-1] for x in sparse]
	return Adj, sparse

#Parse method 1
#
#@input path<string>: path to raw data file
#@return Adj<list<list<int>>>: Adjacency matrix
#@return sparse<list<int>>: list of sparse edges
#
def parse_method3(path):
	with open(path, 'r') as f:
		data = f.readlines()
	Adj = data[0].strip()[1:-3].split(';')
	Adj = [x.strip().split(',') for x in Adj]
	Adj = [[int(y.strip()) for y in x] for x in Adj]
	index = 1
	sparse = []
	start = False
	for ii in range(index, len(data)):
		if start:
			sparse.append(data[ii].strip())
		elif 'Found' in data[ii]:
			start = True
	sparse = [x.split(':')[1].strip() for x in sparse]
	sparse = [[int(x.split('<')[0].strip()) -1, int(x.split('>')[1].strip())-1] for x in sparse]
	return Adj, sparse

def parse_method4(path):
	with open(path, 'r') as f:
		data = f.readlines()
	Adj = []
	sparse = []
	s_mode = False
	for d in data:
		d = d.strip()
		if d == 'Sparse Edges:':
			s_mode = True
		else:
			if s_mode:
				sparse.append([int(d.split('<')[0].strip()), int(d.split('>')[1].strip())])
			else:
				Adj.append([float(x) for x in d.split('\t')])
	return Adj, sparse

#Writes parsed data into correct format for loading
#
#@input base_path<string>: base path to directory
#@input Adj<list<list<int>>>: adjacency matrix
#@input sparse<list<int>>: list of sparse edges
#
def save_parsed_data(base_path, Adj, sparse):
	path_lib.create_path(base_path)
	with open(os.path.join(base_path, 'adjacency.txt'), 'w') as f:
		for row in Adj:
			f.write("\t".join([str(x) for x in row]))
			f.write("\n")
	with open(os.path.join(base_path, "labels.txt"), "w") as f:
		for v in range(len(Adj)):
			f.write('{}\n'.format(v))
	with open(os.path.join(base_path, 'sparse.txt'), 'w') as f:
		for e in sparse:
			f.write('{}\t{}\n'.format(e[0], e[1]))

def process_single_file(raw_path, graph_path, file, parse1, parse2, parse3, parse4):
	src_path = os.path.join(raw_path, file)
	folder_name = path_lib.get_filename_without_extension(file)
	base_path = os.path.join(graph_path, folder_name)

	if parse1:
		Adj, sparse_edges = parse_method1(src_path)
	elif parse2:
		Adj, sparse_edges = parse_method2(src_path)
	elif parse3:
		Adj, sparse_edges = parse_method3(src_path)
	elif parse4:
		Adj, sparse_edges = parse_method4(src_path)

	save_parsed_data(base_path, Adj, sparse_edges)

#Runs the parser
#
#@input raw_path<string>: path to base raw files
#@input graph_path<string>: folder to output graph files
#@input file<string>: input file
#@input parse1<boolean>: parse using method 1
#@input parse2<boolean>: parse using method 2
#@input parse3<boolean>: parse using method 3
#
def run(raw_path, graph_path, file, parse1, parse2, parse3, parse4, process_all):
	if (file == '' and not process_all) or not (parse1 or parse2 or parse3 or parse4):
		print("Please set desired file and parsing method")
		sys.exit(-1)
	if process_all:
		files = path_lib.get_all_files_in_directory(raw_path)
		for file in files:
			p = os.path.join(graph_path, path_lib.get_filename_without_extension(file))
			if not path_lib.directory_exists(p):
				process_single_file(raw_path, graph_path, file, parse1, parse2, parse3, parse4)	
	else:
		process_single_file(raw_path, graph_path, file, parse1, parse2, parse3, parse4)

#ARGUMENT CONTROLLER
description = 'Converts raw data output of matlab to visualization ready data'
raw_path = os.path.join(global_paths.data, 'modules', 'reddit_crawler', 'raw_results')
graph_path = os.path.join(global_paths.data, 'modules', 'reddit_crawler', 'graphs')
f = ''

arg_vars = {
	'raw_path': {'help': "Base path to raw files", 'value': raw_path},
	'graph_path': {'help': "Base path to graph folder", 'value': graph_path},
	'file': {'help': "File to load", 'value': f}
}
flag_vars = {
	'parse1': {'help': 'Parse based on Sahil input', 'value': True},
	'parse2': {'help': 'Parse based on Sahil input', 'value': True},
	'parse3': {'help': 'Parse based on Sahil input', 'value':True},
	'parse4': {'help': 'Parse based on Matlab output', 'value': True},
	'process_all': {'help': 'Parses all unprocessed files and ignores errors', 'value': True}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	run(**var_data)