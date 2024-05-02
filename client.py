from twisted.internet.protocol import DatagramProtocol
from twisted.internet.error import CannotListenError 
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from random import randint
from functools import partial
import hashlib
import json
import time

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
        self.connections = []
        self.chats = {}
        self.online = True
        
        # connection settings
        self.myaddr = (host, port)
        self.address = None
        self.toUser = None
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
        # print(message)

        if addr == self.worker:
            if message["header"] == "__PING__":
                self.sendMessage("__PING__", self.username, addr)

            elif message["header"] == "__CONNECT__":

                print("Select a client:")
                for i,u in enumerate(message["message"]):
                    print(f" ({i+1}):", u)

                self.connections = list()

                for a in message["message"]:
                    self.connections.append({ 'value':f'{a[1]}:{a[2]}', 'label':f'{a[0]}' })
                    
                # print(self.connections)
                def connectTo():
                    index = None
                    while self.address == None:
                        try:
                            index = int(input("select an address\nEnter -1 to reload\nEnter -2 to display messages\n>> "))
                            if index == -1:
                                self.sendMessage("__INIT__", "", self.worker)
                                return
                            if index == -2:
                                print("Users:")
                                for u in self.chats.keys():
                                    print(u)

                                try:
                                    u = input("select a user by name\n>> ")

                                    for chat in self.chats[u]:
                                        print(chat[2],":",chat[3])
                                        
                                except:
                                    pass

                                self.sendMessage("__INIT__", "", self.worker) 
                                return

                            self.address = (message["message"][index-1][1], message["message"][index-1][2])
                            self.toUser = message["message"][index-1][0]
                            
                            if self.chats.get(self.toUser) == None:
                                self.chats[self.toUser] = []

                        except Exception as e:
                            if isinstance(e, EOFError):
                                print("Input EOFError")
                                return
                            
                            index = None
                            continue
                        break

                    self.sendCoRoutine()

                reactor.callInThread(connectTo)
                

            elif message["header"] == "__RELOAD__":
                self.connections = list()
                for a in message["message"]:
                    self.connections.append({ 'value':f'{a[1]}:{a[2]}', 'label':f'{a[0]}' })
                # print(self.connections)

        else:             
           if message["header"] == "__P2P__":
                print(message["username"], ":", message["message"])

                if self.chats.get(message["username"]) == None:
                    self.chats[message["username"]] = []

                self.chats[message["username"]].append((time.time(), time.asctime(), message["username"], message["message"]))
                # print(self.chats[message["username"]])

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
            if self.uuid == None:
                print("unauthorized connection")
                return
            try:
                msg = input(">> ")
                if msg == "::q::":
                    print(f"disconnecting from {self.address[0]}:{self.address[1]}")
                    print('\n\n\n')
                    self.address = None
                    self.sendMessage("__INIT__", "", self.worker)
                    break
                

                if self.chats.get(self.toUser) == None:
                    self.chats[self.toUser] = []
                self.chats[self.toUser].append((time.time(), time.asctime(), self.username, msg))

                self.sendMessage("__P2P__", msg, self.address)
            except Exception as e:
                if isinstance(e, EOFError):
                    print("Input EOFError")
                    return
                print(e)


def exit_client(client: Client):
    client.online = False
    client.sendMessage("__STOP__", "", client.worker)
    client.listener.stopListening()
    print("Interrupt signal recieved, client stopped")


def start_client(client: Client, testMode=False):
    try:
        client.listener = reactor.listenUDP(client.myaddr[1], client)
        # set up interrupt handler
        handler = partial(exit_client, client)
        reactor.addSystemEventTrigger('before', 'shutdown', handler)

        if not testMode:
            reactor.run()

    except CannotListenError:
        pass


if __name__ == "__main__":
    try:
        client = Client(input("enter your username:\n>> "),"localhost", randint(5000, 9998))
        start_client(client)
    except KeyboardInterrupt:
        print("Exitting")