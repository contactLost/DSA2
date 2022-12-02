from multiprocessing.connection import wait
import channel as channel
import os
import RingNode


chan = channel.Channel()
assert chan.channel.flushall()

client = [RingNode.RingNode() for i in range(1)]

#Initilize data file for writing test
# f = open("./datafile.txt" ,"wt")
# writeFirstLine = "0\n"
# writeSecondLine = "0"
# f.write(writeFirstLine)
# f.write(writeSecondLine)
# f.close()  

#Open Clients
for i in range(1):
    pid = os.fork()
    if pid == 0:
        for j in range(4):
            client[i].writeToFile()
        os._exit(0)

