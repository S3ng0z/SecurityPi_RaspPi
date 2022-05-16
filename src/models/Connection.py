import socket


class Connection:

    

    def __init__(self):
        pass

    """
        @description Method that establishes the communication channel with the socket.
    """
    def connect():
        URL = '192.168.1.33'
        PORT = 8000
        #PORT = 9000
        #clientSocket = socket.socket()
        #clientSocket.connect((self.URL, self.PORT))
        #clientSocket.connect(('192.168.228.31', 8000))
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #clientSocket.connect(('192.168..105', 8000))
        clientSocket.connect((URL, PORT)) #RPi 4
        #clientSocket.connect(('192.168.1.33', 9000)) #RPI 3
        clientSocket.makefile('wb')
        print('clientSocket: ' + str(clientSocket))
        return clientSocket

    def connectSendScreenShoot():
        URL = '192.168.1.33'
        PORT = 8080
        #PORT = 9090
        #clientSocket = socket.socket()
        #clientSocket.connect((self.URL, self.PORT))
        #clientSocket.connect(('192.168.228.31', 8000))
        clientSocket = socket.socket()
        clientSocket.connect((URL, PORT)) #RPi 4
        #clientSocket.connect(('192.168.1.33', 9090)) #RPi 32
        clientSocket.makefile('wb')
        print('clientSocket: ' + str(clientSocket))
        return clientSocket

    """
        @description Method that closes the socket communication channel.
    """
    def closeConn(clientSocket):
        clientSocket.close()