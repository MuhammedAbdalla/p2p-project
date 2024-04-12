import client

c2 = client.Client("TestUser2", "TestPass2", None, 8889)

# c2.sendMsg("Hello", {"ipaddr":"192.168.99.105", "ipport":8889})
c2.__connect__()
