#Runs the demo application

import os

from Digital_Library.lib import arg_lib
from Digital_Library.lib import path_lib

import visualization
import reddit_crawler


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


def _run(base_path, file, results, parse1, parse2, parse3):
	folder = ''
	if results:
		folder = 'Results'
	data_path = os.path.join(base_path, folder, file)

	if parse1:
		Adj, sparse_edges = parse_method1(data_path)
	elif parse2:
		Adj, sparse_edges = parse_method2(data_path)
	elif parse3:
		Adj, sparse_edges = parse_method3(data_path)

	with open('temp.txt', 'w') as f:
		for row in Adj:
			f.write("\t".join([str(x) for x in row]))
			f.write("\n")
	with open('temp.labels', 'w') as f:
		for v in range(len(Adj)):
			f.write('{}\n'.format(v))
	with open('temp.sparse', 'w') as f:
		for e in sparse_edges:
			f.write('{}\t{}\n'.format(e[0], e[1]))

	log_path = os.path.join(base_path, 'logs', 'log.log')
	data_path = os.path.join(base_path, 'Demo')
	visualization.run(log_path, data_path, 'temp.txt', 'temp.labels', sparse_edges, True, False)


#ARGUMENT CONTROLLER
description = 'Demo'
base_p = 'D:\\Digital_Library\\data\\Documents\\Class\\CS_592_Compressive_Sensing\\Project'
f = ''

arg_vars = {
	'base_path': {'help': "Base path for data", 'value': base_p},
	'file': {'help': "File to load", 'value': f}
}
flag_vars = {
	'results': {'help': 'Load from results folder', 'value': True},
	'parse1': {'help': 'Parse based on Sahil input', 'value': True},
	'parse2': {'help': 'Parse based on Sahil input', 'value': True},
	'parse3': {'help': 'Parse based on Sahil input', 'value':True}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)