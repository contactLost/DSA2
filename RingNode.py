import os
import channel
import constants
import random
import time
import threading


from datetime import datetime

lock = threading.Lock()
lock2 = threading.Lock()
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
        self.finished = False
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
            #Check end condition
            readed_total_update = self.readTotalUpdate()
            if readed_total_update >= constants.TOTCOUNT:
                print("CLIENT " + self.nodeID + " EXIT.")
                self.ci.changeTokenHolder(self.nextNodeID)
                self.finished = True
            
            self.using = False
            if self.pending_requests:
                self.ci.changeTokenHolder(self.nextNodeID)
                self.pending_requests = False

    def countHungry(self):
        #Hungry counter
        print("countHungry")
        while not self.finished:
            lock.acquire()
            if self.countHunger:
                self.countHunger = False
                startingTime = round(time.time()*1000)
                timer = startingTime

                while timer - startingTime < self.maxTime:
                    timer = timer + 1
                self.hungry = True
                self.countHunger = True
            lock.release()

        lock.acquire()
        if self.ci.checkTokenHolder() == self.nodeID:
            self.ci.changeTokenHolder(self.nextNodeID)
        lock.release()

    def listenRequests(self):
        while not self.finished:
            lock.acquire()
            #Listen to requests
            message = None
            
            message = self.ci.recvFromAny(3)

            #When a request received
            if self.pending_requests or message != None:
                if self.ci.checkTokenHolder() == self.nodeID and not self.using:
                    self.ci.changeTokenHolder(self.nextNodeID)
                else:
                    self.pending_requests = True
                    if (not (self.ci.checkTokenHolder() == self.nodeID)) and (not (self.asked)):
                        print("Node " + self.nodeID + ": " + "Request sent to " + self.previousNodeID)
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
            lock.release()

        lock.acquire()
        if self.ci.checkTokenHolder() == self.nodeID:
            self.ci.changeTokenHolder(self.nextNodeID)
        lock.release()

    def wantResource(self):
        print("wantResource entered")
        while not self.finished:
            lock.acquire()
            #To use resource
            if self.hungry:
                if not (self.ci.checkTokenHolder() == self.nodeID):
                    if not self.asked:
                        self.ci.sendTo([str(self.previousNodeID)], constants.REQ_MSG)
                        self.asked = True
                else:
                    self.using = True
            lock.release()

        lock.acquire()
        if self.ci.checkTokenHolder() == self.nodeID:
            self.ci.changeTokenHolder(self.nextNodeID)
        lock.release()

            

    def tokenReceived(self):
        print("tokenReceived entered")
        while not self.finished:
            lock.acquire()
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
            lock.release()

        lock.acquire()
        if self.ci.checkTokenHolder() == self.nodeID:
            self.ci.changeTokenHolder(self.nextNodeID)
        lock.release()


    

    def run(self):
        self.ci.bind(self.nodeID)
        t1 = threading.Thread(target=self.wantResource)
        t1.start()

        t2 = threading.Thread(target=self.tokenReceived)
        t2.start()

        t3 = threading.Thread(target=self.listenRequests)
        t3.start()

        t4 = threading.Thread(target=self.countHungry)
        t4.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        


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
        f = open(constants.DATAFILE ,"wt")
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
        f = open(constants.LOGFILE,"at")
        f.write(logText)
        f.close()

    def readTotalUpdate(self):
        #open file
        f = open(constants.DATAFILE)
        #read file
        firstLine = f.readline().strip("\n")
        secondLine = f.readline()
        f.close()
        return int(secondLine)