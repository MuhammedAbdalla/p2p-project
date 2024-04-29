from twisted.internet.protocol import DatagramProtocol
from twisted.internet.error import ReactorAlreadyRunning
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from functools import partial
import json
import time


class Worker(DatagramProtocol):
    def __init__(self):
        self.clients = set()
        self.cache = {}
        self.chats = {}
        self.ping = set()
    

    def datagramReceived(self, datagram, addr):
        json_content = datagram.decode("utf-8")
        message = json.loads(json_content)
        print(addr, ":", message)

        if message["header"] == "__INIT__":
            def init():
                self.updateClients()
                print(self.ping)
                while len(self.ping) > 0:
                    time.sleep(0.25)
                
                self.clients.add(addr)

                addresses = self.returnClients(addr)
                self.sendMessage("__CONNECT__", addresses, addr)

            reactor.callInThread(init)
        elif message["header"] == "__OK__":
            print(f"ping received from {addr}")
            self.ping.remove(addr)
            

            
    def updateClients(self):
        for a in self.clients:
            self.sendMessage("__PING__", "", a)
            self.ping.add(a)


    def returnClients(self, addr):
        addresses = set()
        for a in self.clients:
            if a != addr:
                addresses.add(a)
        return list(addresses)


    def sendMessage(self, header, message, addr):
        try:
            # package message into a json and serialize it before encoding
            info = {"username":"SERVER", "header":header, "message":message}
            self.transport.write(json.dumps(info).encode("utf-8"), addr)
            handle = partial(self.handleTimeout, addr)
            if header == "__PING__":
                reactor.callLater(3, handle)
            return True
        except:
            return False


    def handleTimeout(self, addr):
        print("Timeout: no response received.")
        self.clients.remove(addr)
        self.ping.remove(addr)


    def __saveData__(self):
        __cache__ = self.__updateCache__()
        with open("db/cache.json", "w") as jsonFile:
            json.dump(__cache__, jsonFile)

    
    def __updateCache__(self):
        __cache__ = {}
        __cache__["clients"] = self.clients
        __cache__["chats"] = self.chats

        return __cache__


def exit_worker(listener, worker: Worker):
    print("Interrupt signal recieved, worker stopped")

    # stop worker listener
    listener.stopListening()


def start_worker():
    try:
        worker = Worker()
        listener = reactor.listenUDP(9999, worker)
        print("worker live 127.0.0.1:9999")
        
        # set up interrupt handler
        handler = partial(exit_worker, listener, worker)
        reactor.addSystemEventTrigger('before', 'shutdown', handler)
    except ReactorAlreadyRunning:
        print("worker already running")


if __name__ == "__main__":
    try: 
        start_worker()
        reactor.run()
    except KeyboardInterrupt:
        print("Exitting")
