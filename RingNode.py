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
        

    def run(self):
        while True:
            #Listen to requests
            message = self.ci.recvFromAny()

            #When a token reveived
            if self.ci.checkTokenHolder() == self.nodeID:
                self.asked = False
                if self.hungry:
                    self.using = True
                    self.hungry = False
                    #Async use file
                else:
                    self.ci.changeTokenHolder(self.nextNodeID)
                    self.pending_requests = False

            #To use resource
            if self.hungry:
                if self.ci.checkTokenHolder() != self.nodeID:
                    if not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
                    # wait until (using == TRUE) migth be unnecessary for us
                else:
                    self.using = True

            #Release resource
            self.using = True
            if self.pending_requests:
                self.ci.changeTokenHolder(self.nextNodeID)
                self.pending_requests = False

            #When a request received
            if message == constants.REQ_MSG:
                #Delete all requests received
                if self.ci.changeTokenHolder == self.nodeID and not self.using:
                    self.ci.changeTokenHolder(self.nextNodeID)
                else:
                    self.pending_requests = True
                    if self.ci.changeTokenHolder == self.nodeID and not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
    
            #Hungry counter

            #Check end condition

            # try:
            #     self.ci.bind(self.nodeID)

            #     # print("CLIENT " + self.nodeID + " sending message: "+ ("Hello from " +str(self.nodeID)) + "\n")
            #     # self.ci.sendTo([str(self.nextNodeID)],("Hello from " +str(self.nodeID)) )

            #     while True:
            #         message = self.ci.recvFromAny()
            #         if message == None:
            #             continue
            #         print("NODE: " + str(message[0]) + " Received message: " + str(message[1]) +"\n" )
            # except AssertionError as msg:
            #     print("ASSERT", self.nodeID, " msg:" , msg)




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
