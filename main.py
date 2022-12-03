from multiprocessing.connection import wait
import channel as channel
import os
import sys
import RingNode
import constants

NP = sys.argv[1]
DATAFILE = sys.argv[2]
DELTA = sys.argv[3]
TOTCOUNT = sys.argv[4]
LOGFILE = sys.argv[5]
MAXTIME = sys.argv[6]

constants.NP = int(NP)
constants.DATAFILE = DATAFILE
constants.DELTA = int(DELTA)
constants.TOTCOUNT = int(TOTCOUNT)
constants.LOGFILE = LOGFILE
constants.MAXTIME = int(MAXTIME)

chan = channel.Channel()
chan.channel.flushall()

print(MAXTIME)

nodes = [RingNode.RingNode() for i in range(int(NP))]
[nodes[i].getTopology() for i in range(int(NP))]

# #Open Server
# pid = os.fork()
# if pid == 0:
#     server.run()
#     os._exit(0)

# #Open Clients
# for i in range(10):
#     pid = os.fork()
#     if pid == 0:
#         client[i].run()
#         os._exit(0)

