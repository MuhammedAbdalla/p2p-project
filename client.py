import socket
import threading
import json
import hashlib
import logging
import os
import sys
import time

def hashFunction(username, password):
    if username == None or password == None:
        return None
    
    combined_string = username + password
    sha512 = hashlib.sha512()
    sha512.update(combined_string.encode())
    password_hash = sha512.hexdigest()[:64]

    return password_hash

class Client:
    def __init__(self, username=None, password=None, ipaddr=None, port=None):
        self.user = username
        self.passwd = hashFunction(username, password)
        self.ipaddr = ipaddr if ipaddr != None else socket.gethostbyname(socket.gethostname())
        self.ipport = port
        self.neighbors = []
        self.chats = {}
        self.db = f"db/db_{username}.json"
        self.__saveData__()
    

    def __login__(self, username, password):
        # Specify the file path
        # Try to open the file in read mode
        try:
            with open(self.db, 'r') as jsonFile:
                # If the file exists, read its content
                content = json.load(jsonFile)
                print("File content:", content)
                if content["user"] == username and content["passwd"] == hashFunction(username, password):
                    return True
        except FileNotFoundError:
            # If the file doesn't exist, create it and write some content
            self.__saveData__()
            print("File created successfully.")

        return False


    def __saveData__(self):
        __cache__ = self.__updateCache__()
        with open(self.db, "w") as jsonFile:
            json.dump(__cache__, jsonFile)

    
    def __updateCache__(self):
        __cache__ = {}
        __cache__["user"] = self.user 
        __cache__["passwd"] = self.passwd
        __cache__["ipaddr"] = self.ipaddr
        __cache__["neighbors"] = self.neighbors
        __cache__["chats"] =  self.chats

        return __cache__
    

    # THREAD THE BROADCAST PORT
    def __discover__(self):
        # Broadcast settings
        BROADCAST_IP = '255.255.255.255'
        BROADCAST_PORT = self.ipport

        # Create UDP socket
        bsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
         
        bsocket.sendto("__discover__".encode(), (BROADCAST_IP, BROADCAST_PORT))
        print("discovery advertisement sent")

        def recvInfo(bsocket):
            try:
                while True:
                    print("waiting for info..")
                    data, addr = bsocket.recvfrom(1024)
                    print(f"Received message from {addr}: {data}")
                    break
            except KeyboardInterrupt:
                pass   

        broadcastthread = threading.Thread(target=recvInfo, args=(bsocket, ), daemon=True)
        broadcastthread.start()

        bsocket.close()


    def recvMsg(self):
        self.socket.bind((self.ipaddr, self.ipport))
        # print(f"UDP {self.ipaddr}:{self.ipport}")
        try:
            while True:
                print("waiting for data...")
                dataBytes, addr = self.socket.recvfrom(4096)
                data = dataBytes.decode()

                if not data:
                    print('No more data from', addr)

                print('Received:', data)

                if data == "__discover__":
                    info = {"user":self.user, "ipaddr":self.ipaddr, "neighbors":self.neighbors}
                    json_msg = json.dumps(info)
                    self.socket.sendto(json_msg.encode(), addr)
                    self.sendMsg(json_msg, addr)
                if "TESTEC530" in data:
                    self.sendMsg(" ".join(data.split(" ")[1::]), addr)
        except KeyboardInterrupt:
            self.socket.close()


    def sendMsg(self, message, sendTo):
        # Create a socket object
        print(f"sending message: {message}")
        self.socket.sendto(message.encode(), sendTo)
            

    # THREAD THE CONNECTION PORT
    def __connect__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.bind((self.ipaddr, self.ipport))

        recvthread = threading.Thread(target=self.recvMsg, args=(), daemon=True)
        recvthread.start()

        print(f"SESSION CLIENT {self.user} ONLINE")

        commands = {
            "d":self.__discover__,
            "msg":self.sendMsg, 
            "save":self.__saveData__,
            "refresh":self.__updateCache__,
            "login":self.__login__,  
        }

        while True:
            print("enter a command:", "\n\t".join(list(commands.keys())))
            print('\n')
            cmd = input()

            if cmd == "msg":
                msg = input("enter message\n>> ")
                ipaddr = input("enter ip address\n>> ")
                commands[cmd](msg, ipaddr)

            if cmd == "QUIT":
                break
        
        self.socket.close()
        