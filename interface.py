from client import Client

def command(c: Client, ):
    commands = {
        "d":c.__discover__,
        "msg":c.sendMsg, 
        "save":c.__saveData__,
        "refresh":c.__updateCache__,
        "login":c.__login__,  
    }

    return c

    while True:
        print("enter a command:", "\n\t".join(list(commands.keys())))
        cmd = input()

        if cmd not in commands:
            continue

        if cmd == "msg":
            msg = input("enter message\n>> ")
            ipaddr = input("enter ip address\n>> ")
            command()[cmd](msg, {"ipaddr":ipaddr, "ipport":8889})