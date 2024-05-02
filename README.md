# Peer-to-Peer project
My implementation of th P2P project was in command line based application. Using Python and the twisted.internet library, this application achives UDP transmission of messages without a persistent connection, or a server to central server <br>
The architecture of this project consists of clients

## Goal of the project
to be able to create a server-less messaging application using any frameworks.

    - Discovery & Login
    - session connection
    - chat
    - file exchange
    - local db
    - offline synch

<hr>

## Files 
``` app.py ``` <br>
app.py was going to be a webbased implemention of the P2P application initially built in command line <br>
``` client.py ``` <br>
client.py is contains the object class Client, which requires a username, host and port address. <br>
currently every Client object is running on localhost, with addresses ranging from 127.0.0.1:5000 to 127.0.0.1:9998 <br>
``` worker.py ``` <br>
worker.py contains object class Worker, which runs soley to intialize Client object, return active clients from PING messages, and removing clients upon exit. <br>

## Run The Application
To run this project you need to.

1. start the worker client by running ```python worker.py``` one terminal window
2. start as many clients on as many terminal windows. One client per terminal ```python client.py```
3. Follow the instructions on the command prompt
<br>

### Connecting to users

![image](https://github.com/MuhammedAbdalla/p2p-project/assets/54071115/7640aef6-a492-450c-a538-e31e52a3bc64) <br>
the command prompt will ask you to type the index the user's address is listed. <br><br>

![image](https://github.com/MuhammedAbdalla/p2p-project/assets/54071115/4095d435-04ce-44ff-a21e-ca7618c9cc99) <br>
User address can be reloaded by inputting -1 <br><br>

### Example Chat

![image](https://github.com/MuhammedAbdalla/p2p-project/assets/54071115/87fd8629-1d65-4d10-a5e2-fe440c41d224) <br>
In the example above, two clients connect and messaging each other. One client exits and returns to the connection prompt. they chose to load past conversations by inputting -2 <br>
All clients have storage for all chats with past users during their session. Chats are saved until the terminal window is closed <br>

### Worker client

![image](https://github.com/MuhammedAbdalla/p2p-project/assets/54071115/5cc96b9b-6c30-446e-81b7-0d15d54ef4d9) <br>
The worker client running on 127.0.0.1:9999 is responsible for handling 

  ```
    __INIT__    :    Initialize Client objects with username, host, port
    __PING__    :    Return username to worker client to indicate client is alive 
    __RELOAD__  :    Invoked by the web page to refresh all connections by pinging clients, 
  ```
  


