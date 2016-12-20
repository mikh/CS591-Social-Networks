#!Python 2.7 source, Fall 2016 Compressive Sensing

import collections

def populate_graph(filename, nodeSize):
    print "Opening", filename, "for graph of size", nodeSize
    adjlist = collections.defaultdict(list)
    dfile = open(filename, 'r')
    for line in dfile.readlines():
        adjlist[len(adjlist)] = (line.split())
    if debug:
        print adjlist[20], len(adjlist[0])

    return adjlist


def adjlist2signal(glist):
    sigX = []
    for k,edgelist in glist.iteritems():
        sigX += edgelist[k:]

    if debug:
        print 'Length of X is', len(sigX)

    return sigX

def getRandomSamples(x):
     

    
debug = 0
adj = populate_graph('../Data/[1] Personal Relationships via Freeman\'s EIES System/EIES.1', 32)    
Xstar = adjlist2signal(adj)
getRandomSamples(Xstar)
