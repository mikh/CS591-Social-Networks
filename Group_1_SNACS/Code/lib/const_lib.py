#This library provides quick access to const paths and defines for different modules. 
#It's primary goal is to eliminate the need for modules to know the pathing used 
#and get data from here

import json
import os
import copy
import platform
from collections import namedtuple

#this is the base path to the Digital_Library structure. This can be changed to work with a
#package that is independent of the Digital_Library
_base_path = "\\".join(os.path.abspath(__file__).split('\\')[:-2])

#Class that the dictionary structure is converted to.
#Made to make things easy in module development
class generic():

	#Initialize the generic object
	#
	#@input self<generic>: self-reference to object
	#@input data<dict>: dictionary structure of the data
	#
	def __init__(self, data):
		self._allkeys = []
		for key in data:
			self._allkeys.append(key)
			if isinstance(data[key], dict):
				setattr(self, key, generic(data[key]))
			elif isinstance(data[key], list):
				data[key] = _convert_list(data[key])
				setattr(self, key, data[key])
			else:
				setattr(self, key, data[key])

	#Converts the generic structure to dictionary format
	#
	#@input self<generic>: self-reference to object
	#@return d<dict>: dictionary representation of generic object
	#
	def to_dict(self):
		d = {}
		for key in self._allkeys:
			v = getattr(self, key)
			if isinstance(v, list):
				d[key] = _convert_list_of_generics(v)
			elif isinstance(v, generic):
				d[key] = v.to_dict()
			else:
				d[key] = v
		return d


	#Returns all the keys stored in this structure. Similar to <dict>.keys()
	#
	#@input self<generic>: self-reference to object
	#@return _allkeys<list<string>>: list of keys stored in object
	#
	def keys(self):
		return self._allkeys

#Non-unique path exception. Triggered if a path key has been reused
#
#@input Exception<Exception>: Base exception class
#@no-test
#
class NonUniquePathException(Exception):
	pass

#Improper dictionary format exception. Triggered if the path dictionary to be 
#loaded is not correct. Specifically, 'name' and 'children' are required in a path
#dict, and no other keys are allowed
#
#@input Exception<Exception>: Base Exception class
#@no-test
#
class ImproperDictionaryFormatException(Exception):
	pass

#Loads paths from a JSON file into a namedtuple of unique path identifiers
#First we convert everything to a regular dictionary, then encode it into generic
#Special keys:
#with-base-path - uses the base_path provided
#digital-library - uses _base_path defined here
#platform-specific - uses platform.node() to choose option
#dl-base - Folder based off of global.paths.json
#dl-data - Folder based off of global.paths.json
#dl-temp - Folder based off of global.paths.json
#dl-lib - Folder based off of global.paths.json
#dl-logs - Folder based off of global.paths.json
#dl-modules - Folder based off of global.paths.json
#dl-config - Folder based off of global.paths.json
#dl-test - Folder based off of global.paths.json
#dl-docs - Folder based off of global.paths.json
#dl-deploy - Folder based off of global.paths.json
#Otherwise, if a key leads to a dict, the dict has to have: 'path', 'children' 
#'path' = path the name leads to
#'children' = dictionary of child paths which will use the previous path as a base
#If not a dict, key has to lead to a string
#
#@input path<string>: path to JSON file
#@input base_path<string>: base path to use with with-base-path identifier
#@return generic_object<generic>: generic object of the paths
#
def load_paths(path, base_path=None):
	with open(path, 'r') as f:
		data = json.load(f)
	global_paths = None

	d = _convert_paths('', {}, data, base_path, global_paths)
	return generic(d)

#Loads the global paths
#
#@return global_paths<generic>: Global path structure
#
def load_global_paths():
	path = os.path.join(_base_path, 'config', 'paths', 'global.paths.json')
	return load_paths(path)

#Loads the paths of a module
#
#@input module_name<string>: Name of the module as it appears in the config directory structure
#@input filename<string>: filename to use for paths file if it isn't path.json
#@return module_paths<generic>: Module path structure
#
def load_module_paths(module_name, filename='path.json'):
	path = os.path.join(_base_path, 'config', 'paths', module_name, filename)
	return load_paths(path)

#Loads a const file in JSON/plain-text format
#
#@input path<string>: path to const file. Assumed to be in JSON format
#@input as_json<boolean>: load the const as a JSON. Otherwise loads as a plain-text file
#@return const<generic/string>: generic const object
#
def load_const(path, as_json=True):
	if as_json:
		with open(path, 'r') as f:
			data = json.load(f)
		return generic(data)
	else:
		with open(path, 'r') as f:
			return f.read()

#Saves const data either to a JSON or a plain-text file
#
#@input path<string>: path to const file
#@input const_data<generic/string>: const data to save
#@input as_json<boolean>: save the file as a JSON. If a generic is passed, attempts to convert it first.
#
def save_const(path, const_data, as_json=True):
	with open(path, 'w') as f:
		f.write(str(const_data))
	if as_json:
		with open(path, 'w') as f:
			json.dump(const_data.to_dict(), f, sort_keys=True, indent=4)

#Loads module const data
#
#@input module_name<string>: name of module to load const for
#@input filename<string>: name of const file 
#@input as_json<boolean>: load the file as a json file
#@input private<boolean>: load from private section
#@return G<generic>: output object
#
def load_module_const(module_name, filename='const.json', as_json=True, private=False):
	base_path = os.path.join(_base_path, 'config', 'defines', module_name)
	if private:
		base_path = os.path.join(base_path, 'private')
	path = os.path.join(base_path, filename)
	return load_const(path, as_json=as_json)

#Saves module const data
#
#@input module_name<string>: name of module to save const to
#@input data<generic>: data to save
#@input filename<string>: name of const file
#@input as_json<boolean>: save as a json file
#@input private<boolean>: save to private section
#
def save_module_const(module_name, data, filename='const.json', as_json=True, private=False):
	base_path = os.path.join(_base_path, 'config', 'defines', module_name)
	if private:
		base_path = os.path.join(base_path, 'private')
	path = os.path.join(base_path, filename)
	save_const(path, data, as_json=as_json)

#PROCESSING FUNCTIONS

#Converts all dictionary keys into a path format so a single-level dictionary can be created.
#If a key is non-unique or the dictionary is badly made, exceptions are raised
#
#@input base<string>: current path
#@input d<dict>: output dictionary
#@input data<dict>: current position in JSON data
#@input base_path<string or None>: user specified base-path
#@input global_paths<generic>: generic structure used to control Digital-Library or derivative relative paths
#@return d<dict>: output dictionary
#
def _convert_paths(base, d, data, base_path, global_paths):
	for key in data:
		if key == 'with-base-path':
			if base_path != None:
				d = _convert_paths(base_path, d, data[key], base_path, global_paths)
			else:
				d = _convert_paths(base, d, data[key], base_path, global_paths)
		elif key == 'digital-library':
			d = _convert_paths(_base_path, d, data[key], base_path, global_paths)
		elif key == 'platform-specific':
			plat = platform.node()
			if plat in data[key]:
				d = _convert_paths(base, d, data[key][plat], base_path, global_paths)
		elif key in ["dl-base", "dl-data", "dl-temp", "dl-lib", "dl-logs", "dl-modules", "dl-config", "dl-test", "dl-docs", "dl-deploy"]:
			if global_paths == None:
				global_paths = load_global_paths()
			d = _convert_paths(getattr(global_paths, key.split('-')[1]), d, data[key], base_path, global_paths)
		else:
			if isinstance(data[key], dict):
				if key in d:
					raise NonUniquePathException()
				dict_keys = data[key].keys()
				if (len(dict_keys) != 2) or (not 'path' in dict_keys) or (not 'children' in dict_keys):
					raise ImproperDictionaryFormatException()

				d[key] = os.path.join(base, data[key]['path'])
				d = _convert_paths(os.path.join(base, data[key]['path']), d, data[key]['children'], base_path, global_paths)
			else:
				if key in d:
					raise NonUniquePathException
				d[key] = os.path.join(base, data[key])
	return d

#Converts all dict elements in a list to generic objects
#
#@input l<list>: list to transform
#@return l<list>: transformed list
#
def _convert_list(l):
	for ii in range(0, len(l)):
		if isinstance(l[ii], dict):
			l[ii] = generic(l[ii])
		elif isinstance(l[ii], list):
			l[ii] = _convert_list(l[ii])
	return l

#Converts list into of generics into a list of dicts
#
#@input l<list>: list to transform
#@return l<list>: transformed list
#
def _convert_list_of_generics(l):
	for ii in range(0, len(l)):
		if isinstance(l[ii], list):
			l[ii] = _convert_list_of_generics(l[ii])
		elif isinstance(l[ii], generic):
			l[ii] = l[ii].to_dict()
	return l

