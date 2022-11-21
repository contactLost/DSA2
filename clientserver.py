from signal import pause
import channel

class Server:
    def __init__(self):
        self.ch = channel.Channel( )
        self.server = self.ch.join("server")
        

    def run(self):
        print("SERVER: Process "+ self.server + " is now server.")
        self.ch.bind(self.server)
        while True:
            message = self.ch.recvFromAny(self.server)
            if message == None:
                continue
            #destinationSet = [str(message[0][0])]
            #if destinationSet[0] == self.server:
            #    continue
            #self.ch.sendTo( destinationSet, "Received" + message[1]) 
            print("SERVER: " + str(message[0]) + " Received message: " + str(message[1]) +"\n" )


class Client:
    def __init__(self):
        self.ci=channel.Channel( )
        self.client=self.ci.join("client")
        self.server=self.ci.subgroup("server")

    def run(self):
        self.ci.bind(self.client)
        print("CLIENT " + self.client + " sending message: "+ ("Hello from " +str(self.client)) + "\n")
        self.ci.sendTo(self.server,("Hello from " +str(self.client)) )
        #print ("CLIENT " + self.client + " got message: " + str(self.ci.recvFrom([self.server[0].decode("ascii")]))+ "\n")
        #self.ci.sendToAll("this is a broadcast from " + self.client) #testing senttoAlls

        