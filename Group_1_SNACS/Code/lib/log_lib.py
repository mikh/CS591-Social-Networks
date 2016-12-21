#Library that makes it easy to log things

import os

from lib import const_lib
from lib import path_lib
from lib import time_lib


#Ensures log file path exists, defines log if undefined, return path to log
#
#@input module_name<string>: name of module. Used to define log file path. If log_filename is undefined, this will be used to determine the logname
#@input log_filename<string or None>: name of log to use. If left at None, module_name.log will be used
#@input append<Boolean>: Append to log, or over-write log if False
#@return path<string>: path to log
#
def define_log_file(module_name, log_filename=None, log_path=None, append=True):
	if log_path == None:
		global_paths = const_lib.load_global_paths()
		path = os.path.join(global_paths.logs, module_name)
		if log_filename == None:
			module_split = module_name.split('\\')
			path = os.path.join(path, module_split[-1] + '.log')
		else:
			path = os.path.join(path, log_filename)
	else:
		path = log_path
	path_lib.create_path(path)
	if not path_lib.file_exists(path) or not append:
		with open(path, 'w') as f:
			f.write('')
	return path

#Adds a string to the log. String is of format [<message_type>] <timestamp>= message
#
#@input log_file<string or list<string>>: path or list of paths to add a message to
#@input message<string>: message to write
#@input message_type<string>: type of message, defaults to info
#@input print_to_console<Boolean>: if message should be printed to console at the same time. Defaults to true
#
def log(log_file, message, message_type='INFO', print_to_console=True):
	if not isinstance(log_file, list):
		log_file = [log_file]
	m = '[{}] {}= {}\n'.format(message_type, time_lib.utc_timestamp(), message)
	for l in log_file:
		with open(l, 'a') as f:
			f.write(m)
	if print_to_console:
		print(message)

#Quick message to indicate the start of a script run. Message of the form: [INFO] <timestamp>= <log-name> started at <timestamp>, unless m is specified
#
#@input log_file<string or list<string>>: path or list of paths to add a message to
#@input print_to_console<Boolean>: if message should be printed to console at the same time. Defaults to true
#@input m<string>: indicates a message to be printed. If not specified, <log-name> started at <timestamp> is used
#@return timer<int>: Returns the start time in seconds which can be passed to log_end to give a total run-time
#
def log_start(log_file, m='', print_to_console=True):
	timer = time_lib.get_current_time_in_seconds()
	if m == '':
		l = path_lib.get_filename_without_extension(log_file.split('\\')[-1])
		m = '{} started at {}'.format(l, time_lib.utc_timestamp())
	log(log_file, m, print_to_console=print_to_console)
	return timer

#Quick message to indicate the end of a script run. Message of the form: [INFO] <timestamp>= <log-name> ended at <timestamp> (<duration>s)
#
#@input log_file<string or list<string>>: path or list of paths to add a message to
#@input m<string>: indicates a message to be printed. If not specified, <log-name> ended at <timestamp> is used
#@input print_to_console<Boolean>: if message should be printed to console at the same time. Defaults to true
#@input timer<int>: Optionally takes in the start time in seconds which is used to calculate the total run-time
# 
def log_end(log_file, m='', print_to_console=True, timer=None):
	if m == '':
		l = path_lib.get_filename_without_extension(log_file.split('\\')[-1])
		m = '{} ended at {}'.format(l, time_lib.utc_timestamp())
	if timer != None:
		t = time_lib.get_current_time_in_seconds() - timer
		m += ' ({}s)'.format(t)
	log(log_file, m, print_to_console=print_to_console)
