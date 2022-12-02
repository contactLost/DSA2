import channel

class RingNode:

    nodeID : str
    previousNodePID: str
    nextNodePID: str
    token: bool

    def __init__(self):
        self.ci=channel.Channel( )
        successfulInit = False
        while not successfulInit:
            try:
                self.nodeID=self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                print("Could not get ID retrying")

    def run(self):
        try:
            self.ci.bind(self.nodeID)

            (head,next,prev) = self.getTopology()
            print("CLIENT " + self.nodeID + " sending message: "+ ("Hello from " +str(self.nodeID)) + "\n")
            self.ci.sendTo([str(next)],("Hello from " +str(self.nodeID)) )

            while True:
                message = self.ci.recvFromAny()
                if message == None:
                    continue
                print("NODE: " + str(message[0]) + " Received message: " + str(message[1]) +"\n" )
        except AssertionError as msg:
            print("ASSERT", self.nodeID, " msg:" , msg)

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
            nextNodePID =  topologyByteList[0] 
        else:
            nextNodePID =  topologyByteList[thisNodeIndex +1] 

        #Find prev node. If this is the first node. Go to circle's last member
        if thisNodeIndex-1 < 0:
            previousNodePID =  topologyByteList[len(topologyByteList)-1]
        else:
            previousNodePID =  topologyByteList[thisNodeIndex -1] 

        #print("CLIENT " + self.nodeID, nextNodePID, previousNodePID, head)
        return(head,nextNodePID,previousNodePID)

