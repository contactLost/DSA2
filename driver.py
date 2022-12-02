from multiprocessing.connection import wait
import channel as channel
import os
import RingNode


chan = channel.Channel()
assert chan.channel.flushall()

client = [RingNode.RingNode() for i in range(10)]

#Open Clients
for i in range(10):
    pid = os.fork()
    if pid == 0:
        client[i].run()
        os._exit(0)

