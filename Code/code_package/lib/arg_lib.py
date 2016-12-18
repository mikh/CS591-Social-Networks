#This module is intended to simplify the handling of command line arguments using the argparse module. Much of the code that is used to handle arguments is repeated with only an input of generally straightforward variables and help methods

import argparse

#Argument Controller class in charge of maintaining the argparse variable
class ArgumentController():

	#Initializes ArgumentController and defines the argparse module
	#
	#@input self<ArgumentController>: self reference to object
	#@input description<string>: String that is printed on help to describe the module
	#@input printpaths<Boolean>: Defines if printpaths sequence should be added. This is in addition to a regular help print
	#@input set_variables<dict>: Dictionary of all variables to include. The dictionary should have the keys be the name of the argument seperated as name_of_argument (this will be converted to Name Of Argument in printpaths) and its value is a dict of {"help": text, "pp":optional_text, 'value'=current_value}
	#@input flag_variables<dict>: Dictionary of all flag variables to include. The dictionary should have the keys be the name of the argument seperated as name_of_argument(this will be converted to Name Of Argument in printpaths) and its value is a dict of {"help": text}
	#
	def __init__(self, description='', printpaths=True, set_variables=None, flag_variables=None):
		self.parser = argparse.ArgumentParser(description=description)
		self.variables = {}
		self.flag_variables = {}
		if printpaths:
			self.parser.add_argument("--printpaths", help="Print default variables to console", action="store_true")
		if set_variables != None:
			self.variables = set_variables
			for key in set_variables:
				name = "--set_{}".format(key)
				self.parser.add_argument(name, help=set_variables[key]['help'])
		if flag_variables != None:
			self.flag_variables = flag_variables
			for key in flag_variables:
				name = "--{}".format(key)
				self.parser.add_argument(name, help=flag_variables[key]['help'], action="store_true")

	#Parses the arguments given on the commandline
	#
	#@input self<ArgumentController>: self reference to object
	#@return var_data<dict>:dictionary of arguments
	#
	def parse_args(self):
		args = self.parser.parse_args()
		if getattr(args, 'printpaths'):
			self._printpaths()
			return None
		else:
			for name in self.variables:
				arg_name = 'set_' + name
				arg_value = getattr(args, arg_name)
				if arg_value != None:
					self.variables[name]['value'] = arg_value
			for name in self.flag_variables:
				arg_value = getattr(args, name)
				self.flag_variables[name]['value'] = arg_value
			return self.get_arguments()

	#Returns the variables and their values
	#
	#@input self<ArgumentController>: self reference to object
	#@return var_data<dict>: dictionary of variable names with values assigned to them
	#
	def get_arguments(self):
		var_data = {}
		for name in self.variables:
			var_data[name] = self.variables[name]['value']
		for name in self.flag_variables:
			var_data[name] = self.flag_variables[name]['value']
		return var_data

	#Outputs the results of printpaths
	#
	#@input self<ArgumentController>: self reference to object
	#
	def _printpaths(self):
		for name in self.variables:
			if 'printpaths_description' in self.variables[name]:
				description = self.variables[name]['pp']
			else:
				description = self.variables[name]['help']
			name_print = name.split('_')
			name_print = " ".join([x[0].upper()+x[1:] for x in name_print])
			print("{} = {}\n\t{}".format(name_print, self.variables[name]['value'], description))
		for name in self.flag_variables:
			if 'printpaths_description' in self.variables[name]:
				description = self.variables[name]['pp']
			else:
				description = self.variables[name]['help']
			name_print = name.split('_')
			name_print = " ".join([x[0].upper()+x[1:] for x in name_print])
			print("{} = {}\n\t{}".format(name_print, self.variables[name]['value'], description))

