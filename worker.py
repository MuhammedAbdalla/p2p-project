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
        self.client_user_translation = {}
        self.cache = {}
        self.chats = {}
        self.ping = set()
        self.alive = True
    

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
        elif message["header"] == "__PING__":
            self.client_user_translation[addr] = message["message"]
            timeout_call = getattr(self, f"{addr}_timeout", None)
            if timeout_call.active():
                timeout_call.cancel()

            try:
                self.ping.remove(addr)
            except:
                pass
        
        elif message["header"] == "__RELOAD__":
            def init():
                self.updateClients()
                print(self.ping)
                while len(self.ping) > 0:
                    time.sleep(0.25)

                addresses = self.returnClients(addr)
                self.sendMessage("__RELOAD__", addresses, addr)
                
            reactor.callInThread(init)
        elif message["header"] == "__STOP__":
            try:
                self.clients.remove(addr)
            except:
                pass
         

    def updateClients(self):
        self.client_user_translation = {}
        for a in self.clients:
            self.sendMessage("__PING__", "", a)
            self.ping.add(a)


    def returnClients(self, addr):
        addresses = set()
        for a in self.clients:
            if a != addr:
                addresses.add((self.client_user_translation[a], a[0], a[1]))
        return list(addresses)


    def sendMessage(self, header, message, addr):
        try:
            # package message into a json and serialize it before encoding
            info = {"username":"SERVER", "header":header, "message":message}
            self.transport.write(json.dumps(info).encode("utf-8"), addr)

            if header == "__PING__":
                self.addTimeout(addr, 5)

            return True
        except:
            return False


    def addTimeout(self, addr, timeout):
        # Add a timeout for a specific operation
        setattr(self, f"{addr}_timeout", reactor.callLater(timeout, self.handleTimeout, addr))


    def handleTimeout(self, addr):
        print(f"Timeout: no response received from {addr}")
        try:
            self.clients.remove(addr)
            self.ping.remove(addr)
        except:
            pass


    def __saveData__(self):
        __cache__ = self.__updateCache__()
        with open("db/cache.json", "w") as jsonFile:
            json.dump(__cache__, jsonFile)

    
    def __updateCache__(self):
        __cache__ = {}
        __cache__["clients"] = self.clients
        __cache__["chats"] = self.chats

        return __cache__


def exit_worker(worker: Worker):
    print("Interrupt signal recieved, worker stopped")
    worker.alive = False
    # stop worker listener
    worker.listener.stopListening()


def start_worker(worker: Worker, testMode=False):
    try: 
        worker.listener = reactor.listenUDP(9999, worker)
        print("worker live 127.0.0.1:9999")
        
        # set up interrupt handler
        handler = partial(exit_worker, worker)
        reactor.addSystemEventTrigger('before', 'shutdown', handler)
        if not testMode:
            reactor.run()
    except ReactorAlreadyRunning:
        print("worker already running")


if __name__ == "__main__":
    try: 
        worker = Worker()
        start_worker(worker)
    except KeyboardInterrupt:
        print("Exitting")