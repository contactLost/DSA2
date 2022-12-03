import channel
import constants
import asyncio
import random
import time
import threading


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
        self.countHunger = True
        self.maxTime = random.randint(0, constants.MAXTIME)

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

    def countHungry(self):
        self.countHunger = False
        startingTime = round(time.time()*1000)
        timer = startingTime

        while timer - startingTime < self.maxTime:
            print(timer - startingTime)
            timer = timer + 1
        self.hungry = True
        self.countHunger = True

    def run(self):
        self.ci.bind(self.nodeID)
        while True:
            print("Node " + self.nodeID + ": " + "did node ask " + str(self.asked))
            #To use resource
            if self.hungry:
                if not (self.ci.checkTokenHolder() == self.nodeID):
                    if not self.asked:
                        print("Request sent from node " + self.nodeID + " to " + self.previousNodeID)
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True

            #When a token recieved
            print("Node " + self.nodeID + ": " + "Who has token: " + self.ci.checkTokenHolder())
            if self.ci.checkTokenHolder() == self.nodeID:
                print("Node " + self.nodeID + ": " + "Token received")
                self.asked = False
                if self.hungry:
                    self.using = True
                    self.hungry = False
                    print("Node " + self.nodeID + ": " + "Work done")

                    #Release resource
                    self.releaseResource()

                else:
                    self.ci.changeTokenHolder(self.nextNodeID)
                    self.pending_requests = False

            #Listen to requests
            message = self.ci.recvFromAny(3)

            #When a request received
            if self.pending_requests or message != None:
                print("Node " + self.nodeID + ": " + "Request recieved")
                if self.ci.checkTokenHolder() == self.nodeID and not self.hungry:
                    self.ci.changeTokenHolder(self.nextNodeID)
                else:
                    self.pending_requests = True
                    if (not (self.ci.checkTokenHolder() == self.nodeID)) and (not (self.asked)):
                        print("Node " + self.nodeID + ": " + "Request sent to " + self.previousNodeID)
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
    
            #Hungry counter
            if self.countHunger:
                x = threading.Thread(target=self.countHungry)
                x.start()

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
