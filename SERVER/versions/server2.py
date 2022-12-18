import io
import socket
import struct
from io import BytesIO
from PIL import Image
from PIL import UnidentifiedImageError
from PIL import ImageFile
import matplotlib.pyplot as pl
import cv2
import pickle
from threading import Thread, Event
import tempfile
import os
import zipfile
import socketserver
import time


class RecieveScreenShotHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print('Accept connection from {}'.format(self.client_address))

    def handle(self):
        payload_size = struct.calcsize(">L")
        
        img = None
        
        if not os.path.isdir('./frame_container'):
            os.mkdir('./frame_container')

        while True:
            try:
                data = b""
                while len(data) < payload_size:
                    data += self.request.recv(4096)
                print('@@JAGS payload_size: ' + str(payload_size))
                print('@@JAGS data: ' + str(data))

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]
                print('@@JAGS msg_size: ' + str(msg_size))

                while len(data) < msg_size:
                    data += self.request.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                print('@@JAGS data: ' + str(len(data)))
                frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                tempName = next(tempfile._get_candidate_names())
                cv2.imwrite('./frame_container/'+str(tempName)+'.jpg', frame)
                print('@@JAGS recibido')
                time.sleep(0.25)
                '''
                buf = self.request.recv(file_head_size)
                print('@@JAGS file_head_size: ' + str(len(buf)))
                if buf:
                    timestamp, file_size = struct.unpack('24si', buf)
                    received_size = 0
                    data = b''
                    print('@@JAGS file_size: ' + str(file_size))
                    while not received_size == file_size:
                        result = file_size - received_size
                        print('@@JAGS file_size: ' + str(file_size) + ' received_size: ' + str(received_size) + ' RESULT: ' + str(result))
                        if file_size - received_size > 1024:
                            data += self.request.recv(1024)
                            received_size += 1024
                        else:
                            print('Last package: ' + str(result))
                            data += self.request.recv(file_size - received_size)
                            received_size = file_size
                    print('@@JAGS received_size: ' + str(received_size))
                    print('@@JAGS data1: ' + str(len(data)))
                    data = BytesIO(data)
                    print('@@JAGS data2: ' + str(data))
                    try:
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        with Image.open(data) as f:
                            tempName = next(tempfile._get_candidate_names())
                            frame = f.convert('RGB')
                            f.save('./frame_container/'+str(tempName)+'.jpg')
                    except UnidentifiedImageError as uerr:
                        print('UnidentifiedImageError: ' + str(uerr))
                '''
            except Exception as e:
                print('General Exception: ' + str(e))

class DisplayFramestHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print('Accept connection from {}'.format(self.client_address))
    
    def handle(self):
        
        payload_size = struct.calcsize(">L")
        data = b""
        img = None

        while True:
            try:
                while len(data) < payload_size:
                    data += self.request.recv(4096)

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += self.request.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                if img is None:
                    img = pl.imshow(frame)
                else:
                    img.set_data(frame)
                
                pl.pause(0.25)
                
            except Exception as e:
                print('General Exception: ' + str(e))

'''
def handlerCam(conn, data, payload_size, img):
    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)

        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if img is None:
            img = pl.imshow(frame)
        else:
            img.set_data(frame)
        
        pl.pause(0.25)
        #pl.draw()
'''
'''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    data = b""
    payload_size = struct.calcsize(">L")
    img = None
    print('Connected by', addr)
    
    threads = []

    cam = Thread(target=handlerCam, args=(conn, data, payload_size, img))
    threads.append(cam)
    
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer((HOST, PORT2), ThreadedTCPRequestHandler)
    recieveScreenShoot = Thread(target=server.serve_forever)
    recieveScreenShoot.demon = True

    threads.append(recieveScreenShoot)

    #camTF = Thread(target=self.handlerCAMTensorFlow, args=(killAll,))
    #threads.append(camTF)

    # starting processes
    for thd in threads:
        thd.start()

    # wait until processes are finished
    for thd in threads:#
        thd.join()
    
    gc.collect()
'''

"""
Clase principal que inicia los hilos de la aplicación servidor
"""
class Main:

    @staticmethod
    def run():
        HOST = '192.168.1.41'
        PORT_DISPLAY_FRAMES = 8000
        PORT_RECEIVE_SCREENSHOT = 8080
        try:
            threads = []
            socketserver.TCPServer.allow_reuse_address = True

            displayFramesServer = socketserver.ThreadingTCPServer((HOST, PORT_DISPLAY_FRAMES), DisplayFramestHandler)
            displayFrames = Thread(target=displayFramesServer.serve_forever)
            displayFrames.demon = False

            threads.append(displayFrames)

            recieveScreenShotServer = socketserver.ThreadingTCPServer((HOST, PORT_RECEIVE_SCREENSHOT), RecieveScreenShotHandler)
            recieveScreenShot = Thread(target=recieveScreenShotServer.serve_forever)
            recieveScreenShot.demon = True

            threads.append(recieveScreenShot)

            # starting processes
            for thd in threads:
                thd.start()

            # wait until processes are finished
            for thd in threads:#
                thd.join()
            
            gc.collect()

        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    Main.run()