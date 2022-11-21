from multiprocessing.connection import wait
import channel as channel
import os
import clientserver


chan = channel.Channel()
chan.channel.flushall()


server = clientserver.Server()
client = [clientserver.Client() for i in range(10)]

#Open Server
pid = os.fork()
if pid == 0:
    server.run()
    os._exit(0)

#Open Clients
for i in range(10):
    pid = os.fork()
    if pid == 0:
        client[i].run()
        os._exit(0)

