import socket


class Connection:

    #URL = '192.168.1.33'
    #PORT = 8000

    def __init__(self):
        pass

    """
        @description Method that establishes the communication channel with the socket.
    """
    def connect():
        #clientSocket = socket.socket()
        #clientSocket.connect((self.URL, self.PORT))
        #clientSocket.connect(('192.168.228.31', 8000))
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(('192.168.1.33', 8000))
        clientSocket.makefile('wb')
        clientSocket.send("some more data")

        return clientSocket

    """
        @description Method that closes the socket communication channel.
    """
    def closeConn(clientSocket):
        clientSocket.close()