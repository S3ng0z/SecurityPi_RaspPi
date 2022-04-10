# -*- encoding:utf-8 -*-
from core.Controller import Controller
from models.Connection import Connection
from config import APP_PATH
import gc
import os
import io
import struct
import time
import cv2
import sys
import zipfile
import numpy as np
import tensorflow as tf
import shutil
from threading import Thread, Event
import multiprocessing
from multiprocessing import Manager
from PIL import Image, ImageFile
import PIL
from PIL import UnidentifiedImageError


"""
    Main controller. It will be responsible for program's main screen behavior.
"""
class HomeController(Controller):

    #-----------------------------------------------------------------------
    #        Constructor
    #-----------------------------------------------------------------------
    def __init__(self):
        self.homeView = self.loadView("Home")
        self.homeModel = self.loadModel("Home")
        self.homeModel.openLogging()
    
    
    #-----------------------------------------------------------------------
    #        Methods
    #-----------------------------------------------------------------------
    """
        @description
    """
    def main(self):
        self.homeModel.log('INIT SESSION')
        self.homeModel.log('INIT Update System')
        #self.homeView.loadingUpdates()
        self.homeModel.loadUpdates()
        #self.homeView.completedUpgrades()
        self.homeModel.log('END Update System')
        #self.homeView.welcome()
        self.executeThreads()
        self.homeModel.log('END SESSION')
        #self.homeView.close()

    """
        @description Handler that is called by the thread so that the application uses the OpenCV library for face detection.
    """
    def handlerVideoOpenCV(self):
        clientSocket = self.homeModel.connectSocket()
        
        print('clientSocket: ' + str(clientSocket))
        cap = self.homeModel.openVideo()

        pathHaarcascade = APP_PATH + '/lib/haarcascade_frontalface_default.xml'
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)

        #video.start_preview()
        time.sleep(2)

        # used to record the time when we processed last frame
        prev_frame_time = 0
        
        # used to record the time at which we processed current frame
        new_frame_time = 0

        # font which we will be using to display FPS
        font = cv2.FONT_HERSHEY_SIMPLEX

        stream = io.BytesIO()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        cont = 0
        cont_fps = 1
        total_fps = 0
        avg_fps = 0;
        while(cap.isOpened()):
            # Construct a numpy array from the stream
            ret, image = cap.read()
            #image = cv2.resize(frame, (1280, 720))
            # time when we finish processing for this frame
            new_frame_time = time.time()

            # Calculating the fps
 
            # fps will be number of frame processed in given time frame
            # since their will be most of time error of 0.001 second
            # we will be subtracting it to get more accurate result
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
        
            # converting the fps into integer
            fps = float(fps)
            total_fps += fps
            avg_fps =  total_fps / cont_fps
            cont_fps += 1
            # converting the fps to string so that we can display it on frame
            # by using putText function
            #fps = str(fps)
            avg_fps =  str(avg_fps)
        
            # putting the FPS count on the frame
            cv2.putText(image, avg_fps, (10, 30), font, 1, (100, 255, 0), 3, cv2.LINE_AA)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if(cont % 5 == 0):
                cont = 0
                image = self.homeModel.processImage(image, faceCascade)
                imageToEncode = self.homeModel.encodeImage(image, encode_param)

                size = len(imageToEncode)
                stream.seek(0)
                stream.truncate()

                clientSocket.sendall(struct.pack(">L", size) + imageToEncode)
            cont += 1

            #Waits for a user input to quit the application
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        clientSocket.close()

    """
        @description Handler that is called by the thread so that the application uses the OpenCV library for face detection.
    """
    def handlerCAMOpenCV(self):
        clientSocket = self.homeModel.connectSocket()
        print('clientSocket: ' + str(clientSocket))
        camera = self.homeModel.connectCamera()

        pathHaarcascade = APP_PATH + '/lib/haarcascade_frontalface_default.xml'
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)

        camera.start_preview()
        time.sleep(2)

        # used to record the time when we processed last frame
        prev_frame_time = 0
        
        # used to record the time at which we processed current frame
        new_frame_time = 0

        # font which we will be using to display FPS
        font = cv2.FONT_HERSHEY_SIMPLEX

        stream = io.BytesIO()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        cont = 0
        cont_fps = 1
        total_fps = 0
        avg_fps = 0;
        for frame in camera.capture_continuous(stream, 'jpeg'):

            if(cont % 5 == 0):
                cont = 0
                # Construct a numpy array from the stream
                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                # "Decode" the image from the array, preserving colour
                image = cv2.imdecode(data, 1)
                image = cv2.resize(image, (854, 480))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # time when we finish processing for this frame
                new_frame_time = time.time()

                # Calculating the fps
    
                # fps will be number of frame processed in given time frame
                # since their will be most of time error of 0.001 second
                # we will be subtracting it to get more accurate result
                fps = 1/(new_frame_time-prev_frame_time)
                prev_frame_time = new_frame_time
            
                # converting the fps into integer
                fps = float(fps)
                total_fps += fps
                avg_fps =  total_fps / cont_fps
                cont_fps += 1
            
                # converting the fps to string so that we can display it on frame
                # by using putText function
                #fps = str(fps)
                avg_fps =  str(avg_fps)
            
                # putting the FPS count on the frame
                cv2.putText(image, avg_fps, (10, 30), font, 1, (100, 255, 0), 3, cv2.LINE_AA)


                imageFaceDetected = self.homeModel.processImage(image, faceCascade)
                imageToEncode = self.homeModel.encodeImage(imageFaceDetected, encode_param)

                size = len(imageToEncode)
                stream.seek(0)
                stream.truncate()

                clientSocket.sendall(struct.pack(">L", size) + imageToEncode)
            cont += 1

            #Waits for a user input to quit the application
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        camera.release()
        clientSocket.close()
    
    """
        @description Handler that is called by the thread so that the application uses the TensorFlow library for face detection.
    """
    def handlerCAMTensorFlow(self):
        clientSocket = self.homeModel.connectSocket()
        camera = self.homeModel.connectCamera()
        

        camera.start_preview()
        time.sleep(2)
        
        # Load a (frozen) Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.homeModel.getPathToCKPT(), 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        
        #detection of video
        with detection_graph.as_default():
            with tf.compat.v1.Session(graph=detection_graph) as sess:
                stream = io.BytesIO()
                #while True:
                for frame in camera.capture_continuous(stream, 'jpeg'):
                    # Construct a numpy array from the stream
                    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                    # "Decode" the image from the array, preserving colour
                    image = cv2.imdecode(data, 1)
                    # Resize image
                    imS = cv2.resize(image, (720, 680))

                    imageFaceDetected = self.homeModel.processImagenTF(detection_graph, imS, sess)
                    imageToEncode = self.homeModel.encodeImage(imageFaceDetected)

                    size = len(imageToEncode)
                    stream.seek(0)
                    stream.truncate()

                    clientSocket.sendall(struct.pack(">L", size) + imageToEncode)

                    #Waits for a user input to quit the application
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                camera.release()
                clientSocket.close()

    def sendScreenShoot(self):
        clientSocket = self.homeModel.connectSocketSendScreenShoot()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        file_head_size = struct.calcsize('24si')
        if not os.path.isdir(APP_PATH+'/frame_container'):
            os.mkdir(APP_PATH+'/frame_container')
            os.mkdir(APP_PATH+'/frame_container_copy')
            

        while True:
            path, dirs, files = next(os.walk(APP_PATH+'/frame_container'))
            file_count = len(files)

            if(file_count > 0):
                for filename in os.listdir('./frame_container'):
                    time.sleep(1.5)
                    if filename.endswith(".jpg") or filename.endswith(".png"):
                        if os.path.exists(APP_PATH + '/frame_container/' + filename):
                            timestamp = time.time()
                            '''
                                File head:
                                Head size: '24si' (s means bytes in python or char[] in C,24s is 24 bytes;
                                                    i means int, 4 bytes;
                                                    total 28 bytes)
                                Head content: timestamp, file size
                            '''
                            file_head = struct.pack('24si', bytes(str(timestamp), encoding='utf-8'), os.stat(APP_PATH + '/frame_container/' + filename).st_size)
                            print('@@JAGS ' + str(APP_PATH + '/frame_container/' + filename ) + ' size:' + str(os.stat(APP_PATH + '/frame_container/' + filename).st_size))
                            clientSocket.send(file_head)
                            # Read image and send it
                            
                            with open(APP_PATH + '/frame_container/' + filename, 'rb') as f:
                                data = b""
                                file_size = os.stat(APP_PATH + '/frame_container/' + filename).st_size
                                sended_size = 0;
                                while not sended_size == file_size:
                                    print('@@JAGS '+str(APP_PATH + '/frame_container/' + filename)+' len: ' + str(len(data)))
                                    
                                    if file_size - sended_size > 1024:
                                        data = f.read(1024)
                                        sended_size += 1024
                                    else:
                                        print('Last package: ' + str(file_size - received_size))
                                        data = f.read(file_size - received_size)
                                        sended_size = file_size
                                    '''
                                    if not data:
                                        print('{} send over !'.format(APP_PATH + '/frame_container/' + filename))
                                        break
                                    '''
                                    clientSocket.send(data)
                        else:
                            raise ValueError('index error') 

                    shutil.copyfile(APP_PATH + '/frame_container/' + filename, APP_PATH + '/frame_container_copy/' + filename)
                    os.remove(APP_PATH + '/frame_container/' + filename)
                    
        clientSocket.close()
            

    """
        @description Method that will allow the user to interact with the system
    """
    def executeThreads(self):

        threads = []

        cam = Thread(target=self.handlerCAMOpenCV, args=())
        threads.append(cam)

        sendScreenShoot = Thread(target=self.sendScreenShoot, args=())
        threads.append(sendScreenShoot)

         # starting processes
        for thd in threads:
            thd.start()
    
        # wait until processes are finished
        for thd in threads:#
            thd.join()
        
        gc.collect()