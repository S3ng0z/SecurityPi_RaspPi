from datetime import datetime, date
from config import APP_PATH
import os
import time
import io
import struct
import picamera
import sys
from .Connection import Connection

#import git

path = ''

"""
    Model description
"""
class HomeModel:
    def __init__(self, controller):
        self.homeController = controller
        pass

    def openLogging(self):
        global path
        
        today = date.today()
        filename = 'logging_'+str(today)+'.txt'
        if not os.path.exists(APP_PATH+"/logs"):
            os.makedirs(APP_PATH+"/logs")
        
        path = os.path.join(APP_PATH + "/logs/", filename)
        open(path, 'a+')

    def log(self, info):
        global path
        
        file = open(path, 'a+')
        now = datetime.now()
        line = str(info) + ' - ' + str(now) + '\n'
        
        file.write(line)
        file.close()
    
    def loadUpdates(self):
        os.system('../scripts/executeUpdates.sh')

    def clearCache(self):
        pass

    def workerCAM(self, lproxy):
        '''
        if(lproxy.get('killAll') != 0):
            socket = Connection.connect()
            conn = socket.makefile('wb')
            try:

                camera = picamera.PiCamera()
                camera.vflip = True
                camera.resolution = (1280, 720)
                # Start a preview and let the camera warm up for 2 seconds
                camera.start_preview()
                time.sleep(2)

                stream = io.BytesIO()
                for foo in camera.capture_continuous(stream, 'jpeg'):
                    if(lproxy.get('killAll') == 0):
                        break
                    else:
                        conn.write(struct.pack('<L', stream.tell()))
                        conn.flush()
                        
                        stream.seek(0)
                        conn.write(stream.read())
                        
                        stream.seek(0)
                        stream.truncate()
                
                # Write a length of zero to the stream to signal we're done
                conn.write(struct.pack('<L', 0))

            finally:
                conn.close()
                Connection.closeConn(socket)
        '''
        pass
  
    def workerReviewScreenshots(self, lproxy):
        sys.stdin = open(0)
        try:
            
            n = input("What is your name? ")
            
        except EOFError as e:
            print(e)
        