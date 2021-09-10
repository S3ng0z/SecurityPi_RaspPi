import socket


class Connection:

    URL = '192.168.1.33'
    PORT = 8000

    def __init__(self):
        pass

    def connect(self):

        clientSocket = socket.socket()
        clientSocket.connect((self.URL, self.PORT))

        return clientSocket

    def closeConn(self, clientSocket):
        clientSocket.close()