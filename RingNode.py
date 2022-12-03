import os
import channel
import constants
import random
import time
import threading


from datetime import datetime
class RingNode:


    def __init__(self, starttime):
        self.starttime: datetime = starttime
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
                None
        
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
            timer = timer + 1
        self.hungry = True
        self.countHunger = True

    def run(self):
        self.ci.bind(self.nodeID)
        while True:
            #To use resource
            if self.hungry:
                if not (self.ci.checkTokenHolder() == self.nodeID):
                    if not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True

            #When a token recieved
            if self.ci.checkTokenHolder() == self.nodeID:
                self.asked = False
                if self.hungry:
                    self.using = True
                    self.hungry = False
                    self.writeToFile()

                    #Release resource
                    self.releaseResource()

                else:
                    self.ci.changeTokenHolder(self.nextNodeID)
                    self.pending_requests = False

            #Listen to requests
            message = self.ci.recvFromAny(3)

            #When a request received
            if self.pending_requests or message != None:
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
            



    def writeToFile(self):
        #open file
        f = open(constants.DATAFILE )
        #read file
        firstLine = f.readline().strip("\n")
        print("Node " + self.nodeID + ": " + firstLine)
        secondLine = f.readline()
        print("Node " + self.nodeID + ": " + secondLine)
        f.close()
        
        #write
        f = open("./datafile.txt" ,"wt")
        writeFirstLine = str(int(firstLine) + int(constants.DELTA))+ "\n"
        writeSecondLine = str(int(secondLine) + 1)
        f.write(writeFirstLine)
        f.write(writeSecondLine)
        f.close()
        #Update log file
        self.writeToLog( str(int(secondLine) + 1) )


    def getTopology(self):

        topologyByteList: list = self.ci.subgroup("ring1")

        #Change bytes in list to str
        for i in range(len(topologyByteList)):
            topologyByteList[i] = topologyByteList[i].decode("ascii")

        thisNodeIndex = topologyByteList.index(self.nodeID)
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

    def writeToLog(self, updatedValue):
        #t=0060000ms, pid=1, ospid=34765, new=50100, totalcount, count=17
        t = datetime.utcnow()
        pid = self.nodeID
        ospid = os.getpid()
        logText = "t= " + str((t - self.starttime).total_seconds() * 1000)[:6] + "ms, pid= "+ pid +", ospid= "+ str(ospid)  +", "+ str(constants.TOTCOUNT) +", count="+ updatedValue + "\n"
        #print("trying to open log")
        f = open("./logfile.txt","at")
        f.write(logText)
        f.close()