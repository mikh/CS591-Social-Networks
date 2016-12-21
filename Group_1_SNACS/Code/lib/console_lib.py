#Library used to display special console messages. Currently just a progress bar

import sys
import shutil

from lib import time_lib
from lib import const_lib

module_name = 'lib\\console_lib'
const = const_lib.load_module_const(module_name)
time_stamp_previous = None

#Overwrites the current line with a progress bar. Automatically detects the length of the current window for character lengths. Gives option to determine time since last progress update
#
#@input percentage<float>: floating point value indicating precentage of progress bar to fill. Valid range [0,1]
#@input label<string>: string to display along with percentage. Is filled up to erase any previous messages
#@input end<boolean>: optional flag to indicate progress bar is terminated and adds a newline character at the end of the label
#@return etime<int>: integer indicating the number of seconds taken between this call of update_progress_bar and the previous call
#
def update_progress_bar(percentage, label, end=False):
	global time_stamp_previous
	if percentage > 1:
		percentage = 1
	if percentage < 0:
		percentage = 0
	chars_used = int(float(const.progress_bar_length_in_chars)*percentage)
	s = "\r[{0}{1}] {2:.2f}%: {3}".format(("="*chars_used).replace("\n", ""), (" "*(const.progress_bar_length_in_chars-chars_used)).replace('\n', ''), percentage*100, label)
	dimensions = shutil.get_terminal_size()
	total_size = dimensions.columns
	cur_size = len(s)
	if cur_size > total_size:
		s = s[:total_size]
		cur_size = len(s)
	padding = (" " * (total_size-cur_size)).replace("\n", '')
	if end:
		padding = padding[:-1] + '\n'
	s += padding
	sys.stdout.write(s)
	sys.stdout.flush()
	cur_time = time_lib.get_current_time_in_seconds()
	if time_stamp_previous == None:
		etime = None
	else:
		etime = cur_time - time_stamp_previous
	time_stamp_previous = cur_time
	return etime
