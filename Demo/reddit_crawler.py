#Goes through reddit picking up profiles, obtaining their submission locations, and creating links between multiple profiles based on that. End result is an adjacency matrix

import os 
import sys
import praw
import json
import time
import copy

from Digital_Library.lib import const_lib
from Digital_Library.lib import path_lib
from Digital_Library.lib import arg_lib
from Digital_Library.lib import console_lib
from Digital_Library.lib.log_lib import *

module_name = 'reddit_crawler'

path = const_lib.load_module_paths(module_name)
const = const_lib.load_module_const(module_name)
global_paths = const_lib.load_global_paths()

#Prints the functions available to an object
#
#@input obj<Object>: object to examine
#
def _examine_object(obj):
	[print(x) for x in dir(obj) if x[0] != '_']

#Creates the reddit user agent
#
#@input user_agent<string>: User agent string
#@return reddit<praw.Reddit>: reddit object
#
def _create_user_agent(user_agent):
	return praw.Reddit(user_agent=user_agent)

#Get top submissions from a subreddit
#
#@input reddit<praw.Reddit>: reddit object
#@input subreddit<string>: subreddit name
#@input num_submissions<int>: number of submissions to get
#@input checked_submissions<list<string>>: list of submissions already processed
#@return comments<list<Comment>>: list of comments in the subreddit
#@return checked_submissions<list<string>>: list of submissions already processed
#
def _get_top_submission_comments(reddit, subreddit, num_submissions, checked_submissions):
	comments = []
	submissions = reddit.get_subreddit(subreddit).get_top_from_all(limit=num_submissions)
	submission = next(submissions, None)
	submission_number = 0
	while submission != None:
		console_lib.update_progress_bar(submission_number/num_submissions, 'Processing {} of {} submissions...'.format(submission_number, num_submissions))
		submission_id = submission.fullname
		if not submission_id in checked_submissions: 
			checked_submissions.append(submission_id)
			#submission.replace_more_comments(limit=None, threshold=0)
			c = praw.helpers.flatten_tree(submission.comments)
			comments.extend(c)
			submission = next(submissions, None)
			submission_number += 1
	console_lib.update_progress_bar(1, 'Done processing submissions.', end=True)
	return (comments, checked_submissions)

#Expands a list of comments that may contain MoreComments objects. Recusively calls this function until all comments have been expanded
#
#@input comments<list<praw.objects.MoreComments>>: List of reddit comments. May contain More Comments
#@return comments<list<praw.objects.Comments>>: List of reddit comments with no MoreComments
#
def _expand_MoreComments(comments):
	new_comments = []
	cur_c = 0
	tot_c = len(comments)
	for c in comments:
		console_lib.update_progress_bar(cur_c/tot_c, "Expanding comment {} of {}...".format(cur_c, tot_c))
		if type(c) == praw.objects.MoreComments:
			if c.count > 0:
				expanded_comments = c.comments()
				new_comments.extend(expanded_comments)
		else:
			new_comments.append(c)
		cur_c += 1
	console_lib.update_progress_bar(1, "Done.", end=True)
	if len(new_comments) == len(comments):
		return new_comments
	else:
		return _expand_MoreComments(new_comments)	

#Converts comment list to a list of users
#
#@input comments<list<Comment>>: list of comment objects
#@return users<list<string>>: list of usernames
#
def _convert_comment_list_to_user_list(comments):
	users = []
	cur_com = 0	
	tot_com = len(comments)
	for c in comments:	
		console_lib.update_progress_bar(cur_com/tot_com, "Converting comment {} of {}...".format(cur_com, tot_com))
		try:
			auth = c.author.name
			users.append(auth)
		except AttributeError:
			pass
		cur_com += 1
	console_lib.update_progress_bar(1, "Done", end=True)
	return list(set(users))

#Processes comments expanding MoreComments and converting regular comments to users.
#Combines _expand_MoreComments, _convert_comment_list_to_user_list, and user dict creation code
#
#@input comments<list<praw.objects.MoreComments and praw.objects.Comments>>: List of reddit comments and MoreComments
#@input users<dict>: dictionary object of users
#@input log_file<string>: path to log file
#@input user_file<string>: path to users json file
#
def _convert_comments_to_users(comments, users, log_file, user_file):
	cur_c = 0
	tot_c = len(comments)

	while len(comments) > 0:
		console_lib.update_progress_bar(cur_c/tot_c, "Processing comment {} of {}...".format(cur_c, tot_c))
		c = comments[0]
		del comments[0]
		log(log_file, "Processing comment {} of {}...".format(cur_c, tot_c), print_to_console=False)
		try:
			if type(c) == praw.objects.MoreComments:
				if c.count > 0:
					log(log_file, "Expanding comment...", print_to_console=False)
					expanded_comments = c.comments()
					log(log_file, "{} new comments expanded".format(len(expanded_comments)), print_to_console=False)
					tot_c += len(expanded_comments)
					comments.extend(expanded_comments)
			else:
				try:
					auth = c.author.name
					log(log_file, "User extracted = {}".format(auth), print_to_console=False)
					if not auth in users:
						users[auth] = {'processed':False}
						log(log_file, "Added new user, saving JSON structure...", print_to_console=False)
						with open(user_file, 'w') as f:
							json.dump(users, f, sort_keys=True, indent=4)
					else:
						log(log_file, "User already present.", print_to_console=False)
				except AttributeError:
					log(log_file, "Attribute error when trying to process comment. Likely Author returns None", print_to_console=False)
		except TypeError:
			log(log_file, "Type error when trying to process comment. Likely the buffering error. Let's wait and resume", print_to_console=False)
			time.sleep(30)
		cur_c += 1
	console_lib.update_progress_bar(1, "Done. {} comments processed.".format(tot_c), end=True)


#Get active subreddits for user with number of content additions
#
#@input reddit<praw.Reddit>: reddit object
#@input user<string>: reddit username
#@return subreddits<dict>: dictionary of submitted subreddits with number of submissions
#
def _get_user_subreddits(reddit, user):
	subreddits = {}
	try:
		user = reddit.get_redditor(user)
	except:
		user = None
	if user != None:
		comments = user.get_comments(limit=const.user_comments)
		if comments != None:
			try:
				comment = next(comments, None)
			except:
				comment = None
			cur_c = 0
			while comment != None:
				console_lib.update_progress_bar(cur_c/1000, "Processing comment {}".format(cur_c + 1))
				try:
					sub = comment.subreddit.display_name
					if not sub in subreddits:
						subreddits[sub] = 0
					subreddits[sub] += 1
				except:
					pass
				try:
					comment = next(comments, None)
				except:
					comment = None
				cur_c += 1
			console_lib.update_progress_bar(1, "Processed {} comments".format(cur_c), end=True)
	return subreddits

#Creates an empty square matrix
#
#@input side_length<int>: length of a side of the square
#@input default_val<int>: default value in the matrix
#@return matrix<list<list<int>>>: square matrix
#
def _create_square_matrix(side_length, default_val=0):
	#return [[default_val] * side_length] * side_length
	matrix = []
	for ii in range(side_length):
		row = []
		for jj in range(side_length):
			row.append(default_val)
		matrix.append(row)
	return matrix

#Writes matrix to file
#
#@input matrix<list<list<int>>>: square matrix
#@input output_file<string>: path to output file
#
def _write_matrix(matrix, output_file):
	with open(output_file, 'w') as f:
		for ii in range(0, len(matrix)):
			for jj in range(0, len(matrix[ii])):
				f.write("{}\t".format(matrix[ii][jj]))
			f.write("\n")

#Compares two users and obtains their interest rating
#
#@input users<dict>: dictionary of all users and subreddits
#@input user_x<string>: name of first user
#@input user_y<string>: name of second user
#@return rating<float>: rating value
#
def _interest_map(users, user_x, user_y):
	subreddits_x = users[user_x]['subreddits']
	subreddits_y = users[user_y]['subreddits']

	interest = 0
	for subreddit in subreddits_x:
		if subreddit in subreddits_y:
			interest += min(subreddits_x[subreddit], subreddits_y[subreddit])
	return interest

#Applies knn to row 
#
#@input row<list<float>>: list of floating point values
#@input knn<int>: number of neighbors
#@return row<list<float>>: floating point values
#
def _apply_knn_to_row(row, knn):
	temp_row = []
	for ii in range(0, len(row)):
		temp_row.append([ii, row[ii]])
	temp_row.sort(key=lambda x:x[1])
	temp_row.reverse()
	keep_indices = []
	for ii in range(0, knn):
		keep_indices.append(temp_row[ii][0])
	for ii in range(0, len(row)):
		if not ii in keep_indices:
			row[ii] = 0
	return row

#Runs the crawl_for_user option
#
#@input log_file<string>: path to log file
#@input data_path<string>: path to data directory of stored values
#
def _crawl_for_users(log_file, data_path):
	log(log_file, "Creating reddit user agent")
	reddit = _create_user_agent(const.user_agent)
	
	#Choose subreddit to check
	with open(os.path.join(data_path, 'subreddits.txt'), 'r') as f:
		subreddits = [x.strip() for x in f.readlines()]
	p = os.path.join(data_path, 'checked_subreddits.json')
	if not path_lib.file_exists(p):
		with open(p, 'w') as f:
			f.write("{}")
	with open(os.path.join(data_path, 'checked_subreddits.json'), 'r') as f: 
		checked_subreddits = json.load(f)

	for subreddit in subreddits:
		if not subreddit in checked_subreddits:
			checked_subreddits[subreddit] = []
		checked_submissions = checked_subreddits[subreddit]
		if len(checked_submissions) < const.number_of_submissions:
			log(log_file, "Getting top {} submission comments from {}".format(const.number_of_submissions, subreddit))
			comments, checked_submissions = _get_top_submission_comments(reddit, subreddit, const.number_of_submissions, checked_submissions)
			checked_subreddits[subreddit] = checked_submissions
			log(log_file, "{} comments obtained".format(len(comments)))	

			log(log_file, "Loading current user JSON file...")
			user_file = os.path.join(data_path, 'users.json')
			if not path_lib.file_exists(p):
				with open(p, 'w') as f:
					f.write("{}")
			with open(os.path.join(data_path, 'users.json'), 'r') as f:
				users = json.load(f)

			log(log_file, "Processing all comments...")
			_convert_comments_to_users(comments, users, log_file, user_file)

			console_lib.update_progress_bar(3/4, "Saving checked subreddits list...")
			with open(os.path.join(data_path, 'checked_subreddits.json'), 'w') as f:
				json.dump(checked_subreddits, f, sort_keys=True, indent=4)
			console_lib.update_progress_bar(1, "Done.", end=True)

#Combines all unique users in JSON files in <combine_folder> and the <user_file> and stores the resulting entries in <user_file>
#
#@input log_file<string>: path to log file
#@input data_path<string>: path to data directory of stored values
#@input user_file<string>: name of the users file to use
#@input combine_folder<string>: Folder where we store JSON files to combine with
#
def _combine_JSON_files(log_file, data_path, user_file, combine_folder):
	log(log_file, 'Combining JSON files...')

	log(log_file, 'Loading user_file...')
	p = os.path.join(data_path, user_file)
	with open(p, 'r') as f:
		users = json.load(f)
	tot_u = len(users.keys())
	log(log_file, '{} users loaded'.format(tot_u))

	log(log_file, 'Obtaining JSON filenames...')
	p = os.path.join(data_path, combine_folder) 
	files = path_lib.get_all_files_in_directory_with_extension(p, 'json')
	log(log_file, '{} files found.'.format(len(files)))

	log(log_file, 'Processing files found...')
	for file in files:
		log(log_file, 'Loading {}...'.format(file))
		p = os.path.join(data_path, combine_folder, file)
		with open(p, 'r') as f:
			users_temp = json.load(f)
		log(log_file, 'File contains {} users.'.format(len(users_temp)))

		cur_i = 0
		tot_i = len(users_temp)
		for user in users_temp:
			console_lib.update_progress_bar(cur_i/tot_i, 'Processing user {}, {} out of {}...'.format(user, cur_i, tot_i))
			u_structure = copy.deepcopy(users_temp[user])
			if not user in users:
				users[user] = u_structure
			else:
				if (not users[user]['processed']) and u_structure['processed']:
					users[user] = u_structure
			cur_i += 1
		console_lib.update_progress_bar(1, 'File Processed. {} total users'.format(len(users.keys())), end=True)

	log(log_file, 'Writing user_file...')
	p = os.path.join(data_path, user_file)
	with open(p, 'w') as f:
		json.dump(users, f, sort_keys=True, indent=4)
	log(log_file, 'File written.')

	log(log_file, 'All files processed. {} total users'.format(len(users.keys())))

#Generates a list of users that have not been processed
#
#@input log_file<string>: path to log file
#@input data_path<string>: path to data directory of stored values
#@input user_file<string>: name of the users file to use
#
def _generate_unprocessed_user_list(log_file, data_path, user_file):
	log(log_file, 'Generating unprocessed user list...')

	log(log_file, 'Loading user JSON structure...')
	p = os.path.join(data_path, user_file)
	with open(p, 'r') as f:
		users = json.load(f)
	tot_u = len(users.keys())
	log(log_file, "{} users loaded".format(tot_u))

	unprocessed_users = []
	cur_u = 0
	log(log_file, 'Checking for unprocessed users...')

	for user in users:
		console_lib.update_progress_bar(cur_u/tot_u, 'Checking user {}, {} out of {}...'.format(user, cur_u, tot_u))
		if not users[user]['processed']:
			unprocessed_users.append(user)
		cur_u += 1
	console_lib.update_progress_bar(1, 'Done.', end=True)
	log(log_file, '{} unprocessed users found'.format(len(unprocessed_users)))

	log(log_file, 'Writing unprocessed user list to file...')
	p = os.path.join(data_path, 'unprocessed_user_list.txt')
	with open(p, 'w') as f:
		for u in unprocessed_users:
			f.write("{}\n".format(u))

#Obtains the current filename for user_structure storage
#
#@input storage_path<string>: path to storage structure
#@return user_structure_path<string>: path to user_structure storage file
#
def _get_current_filename_for_storage(storage_path):
	files = path_lib.get_all_files_in_directory_with_extension(storage_path, 'json')
	highest_number = 0
	for file in files:
		if 'user_partial_storage' in file:
			file = file.split('.')
			if int(file[1]) > highest_number:
				highest_number = int(file[1])
	filename = 'user_partial_storage.{}.json'.format(highest_number)
	p = os.path.join(storage_path, filename)
	if not path_lib.file_exists(p):
		with open(p, 'w') as f:
			f.write('{}\n')
	with open(p, 'r') as f:
		data = json.load(f)
	if len(data.keys()) >= const.user_storage_max_users:
		highest_number += 1
		filename = 'user_partial_storage.{}.json'.format(highest_number)
		p = os.path.join(storage_path, filename)
		if not path_lib.file_exists(p):
			with open(p, 'w') as f:
				f.write('{}\n')
	return p

#Processes users as according to script
#
#@input log_file<string>: path to log file
#@input data_path<string>: path to data directory of stored values
#@input user_file<string>: name of the users file to user
#@input combine_folder<string>: Folder where we store JSON files to combine with
#
def _process_users(log_file, data_path, user_file, combine_folder):
	log(log_file, "Creating reddit user agent")
	reddit = _create_user_agent(const.user_agent)

	log(log_file, 'Loading unprocessed user list...')
	p = os.path.join(data_path, 'unprocessed_user_list.txt')
	with open(p, 'r') as f:
		unprocessed_users = f.readlines()

	tot_u = len(unprocessed_users)
	cur_u = 0
	u_s_p = _get_current_filename_for_storage(os.path.join(data_path, combine_folder))
	with open(u_s_p, 'r') as f:
		user_structure = json.load(f)

	while len(unprocessed_users) > 0:
		u = unprocessed_users[0].strip()
		log(log_file, "Processing user {} [{}/{}]...".format(u, cur_u, tot_u))
		user_structure[u] = {}
		user_structure[u]['processed'] = False

		try:
			subreddits = _get_user_subreddits(reddit, u)
			user_structure[u]['processed'] = True
			user_structure[u]['subreddits'] = subreddits
		except TypeError:
			user_structure[u]['processed'] = True
			user_structure[u]['subreddits'] = None

		with open(u_s_p, 'w') as f:
			json.dump(user_structure, f, sort_keys=True, indent=4)
		if len(user_structure.keys()) >= const.user_storage_max_users:
			u_s_p = _get_current_filename_for_storage(os.path.join(data_path, combine_folder))
			with open(u_s_p, 'r') as f:
				user_structure = json.load(f)

		del unprocessed_users[0]
		with open(p, 'w') as f:
			for u in unprocessed_users:
				f.write("{}\n".format(u.strip()))

		cur_u += 1
	console_lib.update_progress_bar(1, "{} users processed".format(cur_u), end=True)

#Converts user interest list into graph data
#
#@input log_file<string>: path to log file
#@input data_path<string>: path to data directory of stored values
#@input user_file<string>: name of the users file to use
#@input knn<string>: variable for using K-nearest neighbors. If 'None', knn not used
#
def _generate_graph(log_file, data_path, user_file, knn):
	log(log_file, 'Loading user JSON structure...')
	p = os.path.join(data_path, user_file)
	if path_lib.file_exists(p):
		with open(p, 'r') as f:
			users = json.load(f)
		tot_u = len(users.keys())
		log(log_file, "{} users loaded".format(tot_u))

		log(log_file, "Creating empty matrix...")
		matrix = _create_square_matrix(tot_u)
		log(log_file, "Empty matrix ready.")

		key_list = list(users.keys())

		full=False
		if knn!=None:
			full=True

		cur_i = 0
		tot_i = int(tot_u/2*(1+tot_u))
		if full:
			tot_i = tot_u*tot_u

		for ii in range(0, len(key_list)):
			initial = ii+1
			if full:
				initial = 0
			for jj in range(initial, len(key_list)):
				if ii != jj:
					user_x = key_list[ii]
					user_y = key_list[jj]
					console_lib.update_progress_bar(cur_i/tot_i, 'Mapping interest between {} and {}...'.format(user_x, user_y))
					matrix[ii][jj] = _interest_map(users, user_x, user_y)
					cur_i += 1
		console_lib.update_progress_bar(1, "Matrix complete.", end=True)

		if const.create_labels:
			log(log_file, "Creating labels for users...")
			o_labels = os.path.join(data_path, "matrix_"+path_lib.get_filename_without_extension(user_file) + '.labels')
			with open(o_labels, 'w') as f:
				for ii in range(0, len(key_list)):
					f.write("{}\n".format(key_list[ii]))
			log(log_file, "Labels created.")

		if knn != 'None':
			log(log_file, 'Using nearest neighbor mapping for knn={}'.format(knn))
			knn = int(knn)
			cur_i = 0
			tot_i = len(key_list)
			for ii in range(0, len(key_list)):
				console_lib.update_progress_bar(cur_i/tot_i, 'Applying KNN-{} to {}...'.format(knn, key_list[ii]))
				matrix[ii] = _apply_knn_to_row(matrix[ii], knn)
				cur_i += 1
			console_lib.update_progress_bar(1, 'Done.', end=True)

		log(log_file, "Writing matrix...")
		o_p = os.path.join(data_path, "matrix_"+path_lib.get_filename_without_extension(user_file) + '.txt')
		_write_matrix(matrix, o_p)
		log(log_file, "Graph generated")

#Runs the script
#
#@input log_path<string>: path to log file to store results of script run
#@input data_path<string>: path to data directory of stored values
#@input user_file<string>: name of the users file to use
#@input knn<string>: variable for using K-nearest neighbors. If 'None', knn not used
#@input combine_folder<string>: Folder where we store JSON files to combine with
#@input crawl_for_users<boolean>: Indicates script should crawl for new usernames
#@input combine_JSON_files<boolean>: Combines all unique users from <combine_folder> with the <user_file>
#@input generate_unprocessed_user_list<boolean>: Generates a list of unprocessed users to compare to
#@input process_users<boolean>: Indicates script should process found usernames and extract interest subreddits
#@input generate_graph<boolean>: Indicates script should process interest chart and generate an adjacency graph
#
def _run(log_path, data_path, user_file, knn, combine_folder, crawl_for_users, combine_JSON_files, generate_unprocessed_user_list, process_users, generate_graph):
	log_file = define_log_file(log_path, log_path=log_path)
	script_timer = log_start(log_file)

	path_lib.create_path(data_path)

	if crawl_for_users:
		_crawl_for_users(log_file, data_path)
	elif combine_JSON_files:
		_combine_JSON_files(log_file, data_path, user_file, combine_folder)
	elif generate_unprocessed_user_list:
		_generate_unprocessed_user_list(log_file, data_path, user_file)
	elif process_users:
		_process_users(log_file, data_path, user_file, combine_folder)
	elif generate_graph:
		_generate_graph(log_file, data_path, user_file, knn)
	else:
		log(log_file, 'ERROR: No options chosen for script!')

	log_end(log_file, timer=script_timer)

#ARGUMENT PARSING CODE
'''
log_p = os.path.join(global_paths.logs, 'modules', module_name, module_name + '.log')
data_p = os.path.join(global_paths.data, 'modules', module_name)
users_file = 'users.json'
k = "None"
combine_f = 'storage'

description = 'Goes through reddit picking up profiles, obtaining their submission locations, and creating links between multiple profiles based on that. End result is an adjacency matrix'
arg_vars = {
	'log_path' : {'help': 'Path to where log data is stored', 'value': log_p},
	'data_path': {'help': 'Path to where data is stored', 'value': data_p},
	'user_file': {'help': "Filename to users file to use in processing and graphing", 'value': users_file},
	'knn'      : {'help': 'Number of nearest neighbors to use', 'value': k},
	'combine_folder': {'help': 'Folder where we store JSON files to combine with', 'value': combine_f}
}
flag_vars = {
	"crawl_for_users" : {"help": "Crawling initiated for usernames", "value": True},
	"combine_JSON_files": {"help": "Combines all unique users from <combine_folder> with the <user_file>", 'value': False},
	"generate_unprocessed_user_list": {"help": "Generates a list of unprocessed users to compare to", "value": False},
	"process_users": {"help": "Processing subreddit interests for users", "value": False},
	"generate_graph": {"help": "Generating interest graph", "value": False}
}

arg_parser = arg_lib.ArgumentController(description=description, set_variables=arg_vars, flag_variables=flag_vars)
var_data = arg_parser.parse_args()
if var_data != None:
	_run(**var_data)
'''