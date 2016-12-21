################ CHANGELOG #####################
#
# v0.0 - 6/5/15 17:13 Initial version. Designed to provide easy ways to use date and time functions
# v0.1 - 6/6/15 23:31 Added function to give the current time in ms since the start of unix epoch
# v0.2 - 6/6/15 23:40 Added function to convert from mins to ms
# v0.3 - 6/12/15 10:03 Fixed conversion of get_current_time_in to seconds from ms, and added convert_minutes_to_seconds
# v0.4 - 6/22/15 11:30 Added function to return the current time in changelog format
# v0.5 - 6/22/15 15:06 Added a function to convert seconds to a datetime object
# v0.6 - 6/22/15 15:29 Added a function to get the difference in days between 2 datetime objects
# v0.7 - 6/22/15 15:33 Added a function convert the time (hours, minutes, seconds) to seconds
# v0.8 - 6/22/15 15:44 Added a function to return the current date and to return the date after an offset has been added
# v0.9 - 9/24/15 15:33 Added a function to convert string to a datetime object
# v0.10 - 9/24/15 15:50 Added a function to convert a datetime object to seconds
# v0.11 - 12/28/15 14:32 Added a function to get the current time in ms
# v0.12 - 12/28/15 14:40 Added function to convert milliseconds into hours, minutes, seconds, and milliseconds
# v0.13 - 1/26/16 15:12 Created a timer class to allow for timing
# v0.14 - 1/29/16 13:50 Added timer class fully
# v0.15 - 2/28/16 15:27 Added a timestamp function 
# v0.16 - 3/2/16 11:03 Adding countdown to timer
# v0.17 - 3/3/16 16:49 Updated timer to include a pause and resume functionality (counting is off however)
# v0.18 - 3/3/16 21:12 Fixed the timer counting issue
# v0.19 - 3/4/16 10:23 Added function to convert a word to a seconds value
# v0.20 - 3/10/26 16:20 Updated timestamps to work properly
# v0.21 - 3/12/16 17:19 Added month conversion and generation of time stamp given parameters
# v0.22 - 3/13/16 17:40 Added handling for basic error case
# v0.23 - 4/1/15 0:24 Added function to perform arbitrary timestamp conversion
#
################ END CHANGELOG ################

################ TODO #####################
#
################ END TODO ################


import datetime
import calendar
import time
import pytz
import threading
#import iso8601

#denominations
MILLISECONDS = 1000
SECONDS = 60
MINUTES = 60
HOURS = 24

S_IN_HOUR = MINUTES*SECONDS
S_IN_DAY = HOURS*MINUTES*SECONDS
S_IN_WEEK = 7*S_IN_DAY
S_IN_30_DAY_MONTH = 30*S_IN_DAY

month_conversion ={"January":1, "February":2, "March":3, "April":4, "May":5,"June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', "December"]

#return the current date and time
def get_current_time(timezone=pytz.utc):
	return datetime.datetime.now(tz=timezone)

#returns current time in utc
def utc():
	return datetime.datetime.now(tz=pytz.utc)

#returns a string timestamp
def utc_timestamp():
	return utc().isoformat()

#reads a timestamp in isoformat and converts it to 
#def read_utc_timestamp(timestamp):
#	return iso8601.parse_date(timestamp)

#get a timestamp
def get_timestamp():
	return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

#read into timestamp
def read_into_timestamp(timestamp, t_format):
	return datetime.datetime.strptime(timestamp, t_format)

#convert timestamp to string
def convert_timestamp_to_string(timestamp):
	return timestamp.isoformat()

#create timestamp
def create_timestamp(hour, minute, second, month, day, year):
	return "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}".format(year=int(year),month=int(month),day=int(day),hour=int(hour),minute=int(minute), second=int(second))

#convert timestamp to seconds
def convert_timestamp_to_seconds(timestamp, conversion='%Y-%m-%d %H:%M:%S'):
	x = time.strptime(timestamp, conversion)
	return time.mktime(x)

#convert timestamp using arbitrary indentifer to a time_struct
def convert_timestamp_to_time_struct(timestamp, sequence):
	return time.strptime(timestamp, sequence)

#returns the current date
def get_current_date():
	return datetime.datetime.now().date()

#get current time in seconds
def get_current_time_in_seconds():
	return calendar.timegm(time.gmtime())

#get current time in ms
def get_current_time_in_ms():
	return int(round(time.time()*1000))

#function to do a quick conversion from minutes to ms
def convert_minutes_to_ms(mins):
	return mins * 60 * 1000

#function to do a quick conversion from minutes to seconds
def convert_minutes_to_seconds(mins):
	return mins * 60

#function to convert hours, minutes and seconds to seconds
def convert_time_to_seconds(hours, minutes, seconds):
	return hours * 60 * 60 + minutes * 60 + seconds

#function to convert milliseconds into h,m,s,ms
def convert_millis_to_hmsms(ms):
	h = int(ms/(MILLISECONDS*SECONDS*MINUTES))
	ms = ms % (MILLISECONDS*SECONDS*MINUTES)
	m = int(ms/(MILLISECONDS*SECONDS))
	ms = ms % (MILLISECONDS*SECONDS)
	s = int(ms/MILLISECONDS)
	ms = ms % MILLISECONDS
	return (h, m, s, ms)

#create a printable string from h, m, s, ms
def create_time_string(h=0, m=0, s=0, ms=0):
	return "{0:0>2}:{1:0>2}:{2:0>2}:{3:0>3}".format(h, m, s, ms)

#returns the current time in date time format as used by changelog entries
def get_current_time_changelog():
	d = datetime.datetime.now(pytz.timezone("America/New_York"))
	return d.strftime('%m/%d/%y %H:%M')

#convert a timestamp since seconds into datetime object
def convert_seconds_to_datetime(seconds):
	return datetime.datetime.fromtimestamp(seconds, pytz.utc)

#converts a date/time object to seconds since unix epoch
def convert_datetime_to_seconds(t):
	if isinstance(t, datetime.datetime):
		try:
			return (t - datetime.datetime(1970, 1, 1)).total_seconds()
		except TypeError:
			return (t-datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
	elif isinstance(t, time.struct_time):
		return time.mktime(t)
	return None

#converts a string to a date_time object using a pattern string
def convert_string_to_datetime(string, pattern):
	return time.strptime(string, pattern)

#get the difference in days between two datetimes
def get_difference_in_days(d1, d2):
	d1 = d1.date()
	d2 = d2.date()
	delta = d1-d2
	return delta.days

#converts the a word (day, week, month, hour) to seconds
def convert_word_to_seconds(word):
	word = word.lower()
	if word == 'hour':
		return SECONDS*MINUTES
	elif word == 'day':
		return S_IN_DAY
	elif word == 'week':
		return S_IN_WEEK
	elif word == 'month':
		return S_IN_30_DAY_MONTH
	return None

#converts a given value of seconds to a word
def convert_seconds_to_word(s):
	if s == SECONDS*MINUTES:
		return 'hour'
	elif s == S_IN_DAY:
		return 'day'
	elif s == S_IN_WEEK:
		return 'week'
	elif s == S_IN_30_DAY_MONTH:
		return 'month'
	return None

#returns a date object of the date offset by the days
def get_date_offset(d, days):
	return d + datetime.timedelta(days=days)

#timer class
class timer():
	def __init__(self, start_count_ms=0, count_up=True, callback_function=None, callback_delay=0):
		self.start_time = get_current_time_in_ms()
		self.last_checked_time = self.start_time
		self.callback_function=callback_function
		self.paused = True
		self.total_elapsed_time = 0

		self.display_time = start_count_ms
		self.multiplier = 1
		if not count_up:
			self.multiplier = -1
		if callback_function != None:
			self.t_event = threading.Timer(callback_delay, lambda:callback_function())
			self.callback_delay = callback_delay

	def start_timer(self):
		self.paused = False
		self.start_time = get_current_time_in_ms()
		self.last_checked_time = self.start_time
		if self.callback_function != None:
			self.t_event.start()

	#gets either the total elapsed time, or the elapsed time since the last check
	def get_elapsed_time(self, total=False):
		if total:
			t = get_current_time_in_ms() - self.start_time
		else:
			t = get_current_time_in_ms() - self.last_checked_time
		self.last_checked_time = get_current_time_in_ms()
		return t

	#encodes get_elapsed_time into a time_string
	def get_elapsed_time_string(self, total=False):
		if not self.paused:
			self.display_time += self.multiplier * self.get_elapsed_time(total=False)
		(h, m, s, ms) = convert_millis_to_hmsms(self.display_time)
		return create_time_string(h=h, m=m, s=s, ms=ms)

	#pauses running timer
	def pause_timer(self):
		self.display_time += self.multiplier * self.get_elapsed_time(total=True)
		self.total_elapsed_time += self.get_elapsed_time(total=True)
		self.paused = True
		if self.callback_function != None:
			self.t_event.cancel()

	#resumes running timer
	def resume_timer(self):
		self.start_time = get_current_time_in_ms()
		self.last_checked_time=self.start_time
		self.paused = False
		if self.callback_function != None:
			self.t_event = threading.Timer(self.callback_delay-self.total_elapsed_time, lambda:self.callback_function())
			self.t_event.start()


#t = timer()
#
#while True:
#	print(t.get_elapsed_time_string())
#	time.sleep(.001)

	
#t = get_current_time()
#print(t)
#l = dir(t)
#for k in l:
#	print(k)
#print('\n\n')
#print("day", t.day)
#print("hour", t.hour)
#print("usec", t.microsecond)
#print("min", t.min)
#print("minute", t.minute)
#print("month", t.month)
#print("second", t.second)
#print("weekday", t.weekday())
#print("year", t.year)