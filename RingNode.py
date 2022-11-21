import channel

class RingNode:

    previousNodePID: int
    nextNodePID: int
    token: bool

    def __init__(self):
        self.ci=channel.Channel( )
        self.client=self.ci.join()

    def run(self):
        self.ci.bind(self.client)
        getPreviousNode()
        getNextNode()


        #print("CLIENT " + self.client + " sending message: "+ ("Hello from " +str(self.client)) + "\n")
        #self.ci.sendTo(self.server,("Hello from " +str(self.client)) )