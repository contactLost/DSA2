from random import randint
import channel
from threading import Thread, Event
from time import sleep


class RingNode:

    nodeID : str
    previousNodePID: str
    nextNodePID: str

    token: bool = False
    hungry: bool = False
    using: bool = False
    asked: bool = False
    pending_requests: bool = False
    MAX_TIME = 6
    TOTCOUNT = 15

    def __init__(self):
        self.ci=channel.Channel( )
        successfulInit = False
        while not successfulInit:
            try:
                self.nodeID=self.ci.join("ring1")
                successfulInit = True
            except(AssertionError):
                print("Could not get ID retrying")
        self.ci.bind(self.nodeID)

    def run(self):

        try:
            #init token first time
            (head,next,prev) = self.getTopology()
            if(str(head) == self.nodeID):
                self.token = True

            # This code snippet gets prev, next and head node IDs then sends a message to next node.
            #(head,next,prev) = self.getTopology()
            #print("CLIENT " + self.nodeID + " sending message: "+ ("Hello from " +str(self.nodeID)) + "\n")
            #self.ci.sendTo([str(next)],("Hello from " +str(self.nodeID)) )
            stopL = False
            stopH = False
            tListen = Thread( target=self.listen , args=(stopL,))
            tHungry = Thread( target=self.getHungry , args=(stopH,))
            tListen.start()
            tHungry.start()

            while True:

                if(self.hungry == True):
                    if(self.token == True):
                        #Do Job
                        count = self.writeToFile()
                        if(self.TOTCOUNT == count):
                            break
                    else: #If does not have token request it.
                        self.requestToken()
                elif(self.pending_requests): #Not hungry and another node requested
                    if(self.token == True):
                        self.passToken()
                else:
                    continue


        except AssertionError as msg:
            print("ASSERT", self.nodeID, " ERROR msg:" , msg)
        finally:
            #send exit signal
            self.exitSignal()
            stopL = True
            stopR = True
            #self.ci.leave()

    #File has to be initilized with 0\n 0 TODO make it runable with an empty file.
    def writeToFile(self,fileName: str = "",delta: str = 100):
        #open file
        f = open("./datafile.txt" )
        #read file
        firstLine = f.readline().strip("\n")
        #print(firstLine)
        secondLine = f.readline()
        #print(secondLine)
        f.close()
        
        #write
        f = open("./datafile.txt" ,"wt")
        writeFirstLine = str(int(firstLine) + int(delta))+ "\n"
        writeSecondLine = str(int(secondLine) + 1)
        f.write(writeFirstLine)
        f.write(writeSecondLine)  
        #print(writeFirstLine)
        #print(writeSecondLine)
        #close file
        f.close()
        return writeSecondLine

    #Gets topology from redis.
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

    def listen(self, stopL):
        
        while not stopL:
            #Unmarshall message
                message = self.ci.recvFromAny()
                if message == None:
                    continue
                if str(message[1]) == "TOKEN":       #When token comes form right
                    self.token = True
                    self.asked = False
                if str(message[1]) == "REQUEST":     #When request comes from left
                    self.pending_requests = True

                print("NODE: " + str(message[0]) + " Received message: " + str(message[1]) +"\n" )

    def getHungry(self, stopH):
        while not stopH:
            sleep(randint(1,self.MAX_TIME))
            self.hungry=True

    def requestToken(self):
        if not self.asked:
            (head,next,prev) = self.getTopology()
            #print("CLIENT " + self.nodeID + " sending message: "+ ("Hello from " +str(self.nodeID)) + "\n")
            self.ci.sendTo( [str(prev)], ("REQUEST") )
            self.asked = True

    def passToken(self):

            (head,next,prev) = self.getTopology()
            #print("CLIENT " + self.nodeID + " sending message: "+ ("Hello from " +str(self.nodeID)) + "\n")
            self.ci.sendTo( [str(next)], ("TOKEN") )
            self.token = False

    def exitSignal(self):
            (head,next,prev) = self.getTopology()
            self.ci.sendTo( [str(next)], ("EXIT") )