import random
import sys

def get_upper_adj(n):
	f = open('upper_adj_'+str(n)+'.txt', 'w')	
	f.write('[')
	for x in range(n):
		row = []
		for y in range(n):
			if x<y:
				row += [random.randint(0,10)] 
			else:
				row += [0]	
		f.write(str(row)[1:-1]+';')
	f.write ('];')

get_upper_adj(400)
	
