import client
import socket

def test_login():
    c1 = client.Client()
    assert c1.__login__("TestBad", "TestPass") == False

    c2 = client.Client("TestGood", "TestPass")
    assert c2.__login__("TestGood", "TestPass") == True

if __name__ == "__main__":
    # Server IP address and port
    server_address = (socket.gethostbyname(socket.gethostname(), 8889)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send data to the server
    message = "TESTEC530 Muhammed Abdalla!"
    print('Sending:', message)
    sock.sendto(message.encode(), server_address)

    message = "__discover__"
    print('Sending:', message)
    sock.sendto(message.encode(), server_address)

