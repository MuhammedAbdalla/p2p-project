from twisted.internet.protocol import DatagramProtocol
from twisted.internet.error import CannotListenError 
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from random import randint
from functools import partial
import hashlib
import json
import logging


def hashFunction(plaintext):
    if plaintext == None:
        return None
    
    sha512 = hashlib.sha512()
    sha512.update(plaintext.encode())
    hashtext = sha512.hexdigest()[:64]

    return hashtext


class Client(DatagramProtocol):
    def __init__(self, username, host, port):
        if host == "localhost":
            host = "127.0.0.1"

        # user info
        self.username = username
        self.uuid = hashFunction(username)
        self.connections = {}
        self.online = True
        
        # connection settings
        self.addr = (host, port)
        self.address = None
        self.worker = ("127.0.0.1", 9999)
        self.listener = None

        print(f"live on {host}:{port}")


    def startProtocol(self):
        self.sendMessage("__INIT__", "", self.worker)


    # def on_write_success(self, result):
    #     print("Success: ", result)

    
    # def on_write_error(self, failure):
    #     print("Error: ", failure.getErrorMessage())


    # def handle_timeout(self, deferred):
    #     # Timeout callback function
    #     print("Write operation timed out")
    #     # Cancel the deferred to prevent further processing
    #     if not deferred.called:
    #         deferred.cancel()


    def datagramReceived(self, datagram, addr):
        json_content = datagram.decode("utf-8")
        message = json.loads(json_content)
        print(message)

        if addr == self.worker:
            if message["header"] == "__GETUSER__":
                self.sendMessage("__GETUSER__", self.username, addr)

            elif message["header"] == "__CONNECT__":
                print("Select a client\n", message["message"])

                w_addr = None
                w_port = None

                while w_addr == None and w_port == None:
                    try:
                        w_addr = input("write address: ")
                        w_port = int(input("write port: "))
                    except Exception as e:
                        if isinstance(e, EOFError):
                            print("Input EOFError")
                            return
                        
                        w_addr = None
                        w_port = None

                        continue
                    break
                    

                # sanitize input
                self.address = (w_addr, w_port)
                self.connected = False

                # send connection validation to verify connection
                if self.sendMessage("__CONNECT__", "", self.address):
                    self.connected = True
                    reactor.callInThread(self.sendCoRoutine)

            elif message["header"] == "__PING__":
                handle = partial(self.sendMessage, "__OK__", self.online, self.address)
                reactor.callInThread(handle)

        else:
            if message["header"] == "__CONNECT__":
                self.sendMessage("__OK__", "", addr)

            elif message["header"] == "__P2P__":
                print(message["username"], ":", message["message"])


    def sendMessage(self, header, message, addr):
        # package message into a json and serialize it before encoding
        try:
            info = {"username":self.username, "header":header, "message":message}
            self.transport.write(json.dumps(info).encode("utf-8"), addr)
            return True
        except:
            return False


    def sendCoRoutine(self):
        while True:
            self.sendMessage("__P2P__", input(">> ").encode("utf-8"), self.address)



def exit_client(client: Client):
    client.online = False
    client.listener.stopListening()
    print("Interrupt signal recieved, client stopped")

if __name__ == "__main__":
    port = randint(1024, 4096)
    try:
        client = Client("TEST","localhost", port)
        client.listener = reactor.listenUDP(port, client)

        # set up interrupt handler
        handler = partial(exit_client, client)
        reactor.addSystemEventTrigger('before', 'shutdown', handler)

        reactor.run()
    except CannotListenError:
        pass