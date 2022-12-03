import channel
import constants

class RingNode:


    def __init__(self):
        self.ci=channel.Channel()
        successfulInit = False
        self.nodeID = ""
        self.previousNodeID = ""
        self.nextNodeID = ""
        self.hungry = False
        self.pending_requests = False
        self.asked = False
        self.using = False

        while not successfulInit:
            try:
                self.nodeID=self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                print("Could not get ID retrying")
        
    def releaseResource(self):
        #Release resource
        if self.ci.checkTokenHolder() == self.nodeID:
            self.using = False
            if self.pending_requests:
                self.ci.changeTokenHolder(self.nextNodeID)
                self.pending_requests = False

    def run(self):
        self.ci.bind(self.nodeID)
        while True:
            #To use resource
            if self.hungry:
                if self.ci.checkTokenHolder() != self.nodeID:
                    if not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
                    
                    # wait until (using == TRUE) migth be unnecessary for us
                    # while not (self.ci.checkTokenHolder() == self.nodeID):
                    #     print("waiting")

                    #When a token recieved
                    print(self.ci.checkTokenHolder())
                    if self.ci.checkTokenHolder() == self.nodeID:
                        print("Token received at node " + self.nodeID)
                        self.asked = False
                        if self.hungry:
                            self.using = True
                            self.hungry = False
                            print("Work done at " + self.nodeID)

                            #Release resource
                            self.releaseResource()

                        else:
                            self.ci.changeTokenHolder(self.nextNodeID)
                            self.pending_requests = False
                    
                else:
                    self.using = True

            #Listen to requests
            message = self.ci.recvFromAny(3)

            #When a request received
            if message == constants.REQ_MSG:
                if self.ci.checkTokenHolder() == self.nodeID and not self.using:
                    self.ci.changeTokenHolder(self.nextNodeID)
                else:
                    self.pending_requests = True
                    if self.ci.checkTokenHolder() == self.nodeID and not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
    
            #Hungry counter
            self.hungry = True

            #Check end condition
            message = None
            



    def writeToFile(self,fileName: str = "",delta: str = 100):
        #open file
        f = open("./datafile.txt" )
        #read file
        firstLine = f.readline().strip("\n")
        print(firstLine)
        secondLine = f.readline()
        print(secondLine)
        f.close()
        
        #write
        f = open("./datafile.txt" ,"wt")
        writeFirstLine = str(int(firstLine) + int(delta))+ "\n"
        writeSecondLine = str(int(secondLine) + 1)
        f.write(writeFirstLine)
        f.write(writeSecondLine)  
        print(writeFirstLine)
        print(writeSecondLine)
        #close file
        f.close()


    def getTopology(self):

        topologyByteList: list = self.ci.subgroup("ring1")

        #Change bytes in list to str
        for i in range(len(topologyByteList)):
            topologyByteList[i] = topologyByteList[i].decode("ascii")

        thisNodeIndex = topologyByteList.index(self.nodeID)

        #print(topologyByteList)
        head = topologyByteList[0]

        #Find next node. If this is the last node. Go to circle's head
        if thisNodeIndex+1 >= len(topologyByteList):
            self.nextNodeID =  topologyByteList[0] 
        else:
            self.nextNodeID =  topologyByteList[thisNodeIndex +1] 

        #Find prev node. If this is the first node. Go to circle's last member
        if thisNodeIndex-1 < 0:
            self.previousNodeID =  topologyByteList[len(topologyByteList)-1]
        else:
            self.previousNodeID =  topologyByteList[thisNodeIndex -1] 

        print("CLIENT " + self.nodeID, self.nextNodeID, self.previousNodeID, head)
        return(head,self.nextNodeID,self.previousNodeID)
