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
from datetime import datetime


class RecieveScreenShotHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print('Accept connection from {}'.format(self.client_address))

    def handle(self):
        payload_size = struct.calcsize(">L")
        
        img = None
        
        if not os.path.isdir('./frame_container2'):
            os.mkdir('./frame_container2')

        while True:
            try:
                data = b""
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

                tempName = next(tempfile._get_candidate_names())
                cv2.resize(frame, (1280, 720))

                receptionDate = datetime.now()
                textImage = f'\n\n\nReception Date: {receptionDate}'

                y, y0, dy = 10, 80, 20
                for i, line in enumerate(textImage.split('\n')):
                    cv2.putText(frame, line, (10, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                    y = y0 + i*dy
                    
                cv2.imwrite('./frame_container2/'+str(tempName)+'.jpg', frame)
                
                time.sleep(0.25)
                
            except Exception as e:
                print('General Exception RecieveScreenShotHandler: ' + str(e))

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
                frame = cv2.resize(frame, (1280, 720))
                receptionDate = datetime.now()
                textImage = f'\n\n\nReception Date: {receptionDate}'

                y, y0, dy = 10, 80, 20
                for i, line in enumerate(textImage.split('\n')):
                    cv2.putText(frame, line, (10, y ), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
                    y = y0 + i*dy

                #cv2.putText(frame, f'Reception Date: {receptionDate}', (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)

                if img is None:
                    img = pl.imshow(frame)
                else:
                    img.set_data(frame)
                
                pl.pause(0.25)
                
            except Exception as e:
                print('General Exception DisplayFramestHandler: ' + str(e))


"""
Clase principal que inicia los hilos de la aplicación servidor
"""
class Main:

    @staticmethod
    def run():
        #HOST = '192.168.1.96'
        HOST = '192.168.1.96'
        PORT_DISPLAY_FRAMES = 8000 #RPi 4
        PORT_RECEIVE_SCREENSHOT = 8080 #RPI 4
        #PORT_DISPLAY_FRAMES = 9000 #RPi 3
        #PORT_RECEIVE_SCREENSHOT = 9090 #RPI 3
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