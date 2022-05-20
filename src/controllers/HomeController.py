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
from datetime import datetime
from datetime import timedelta


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
            image = cv2.resize(image, (1280, 720))
            # time when we finish processing for this frame
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
            #transmissionDate = datetime.now() + timedelta(hours=1)
            initProcess = datetime.datetime.now() + datetime.timedelta(hours=1)
            initProcess = initProcess.strftime('%H:%M:%S.%f')[:-2]
            avg_fps =  f'Average FPS: {avg_fps:.2f}\nFPS Real: {fps:.2f}\nInit Process: {initProcess}'
            cont_fps += 1
        
            # converting the fps to string so that we can display it on frame
            # by using putText function
            #fps = str(fps)
            y, y0, dy = 20, 20, 40
            for i, line in enumerate(avg_fps.split('\n')):
                cv2.putText(image, line, (10, y ), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                y = y0 + i*dy

            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = self.homeModel.processImage(image, faceCascade)

            endProcess = datetime.datetime.now() + datetime.timedelta(hours=1)
            endProcess = endProcess.strftime('%H:%M:%S.%f')[:-2]

            str_parameters =  f'End Process: {endProcess}'
            cv2.putText(image, str_parameters, (10, 140), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            
            self.homeModel.saveImagen(image)

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

        pathHaarcascade = APP_PATH + '/lib/haarcascade_frontalface_default.xml'
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)

        camera = self.homeModel.connectCamera()
        camera.start_preview()
        time.sleep(2)

        # used to record the time when we processed last frame
        # used to record the time at which we processed current frame
        prev_frame_time, new_frame_time = 0, 0
        
        # font which we will be using to display FPS
        font = cv2.FONT_HERSHEY_SIMPLEX

        stream = io.BytesIO()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        cont, cont_fps, total_fps, avg_fps = 0, 1, 0, 0

        for frame in camera.capture_continuous(stream, 'jpeg'):
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
            transmissionDate = datetime.now() + timedelta(hours=1)
            avg_fps =  f'Average FPS: {avg_fps:.2f}\nFPS Real: {fps:.2f}\nTransmission Date: {transmissionDate}'
            cont_fps += 1
        
            # converting the fps to string so that we can display it on frame
            # by using putText function
            #fps = str(fps)
            y, y0, dy = 20, 40, 20
            for i, line in enumerate(avg_fps.split('\n')):
                cv2.putText(image, line, (10, y ), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                y = y0 + i*dy
                

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
        if not os.path.isdir(APP_PATH+'/frame_container'):
            os.mkdir(APP_PATH+'/frame_container')
            

        while True:
            path, dirs, files = next(os.walk(APP_PATH+'/frame_container'))
            file_count = len(files)

            if(file_count > 0):
                for filename in os.listdir('./frame_container'):
                    time.sleep(1.5)
                    if filename.endswith(".jpg") or filename.endswith(".png"):
                        if os.path.exists(APP_PATH + '/frame_container/' + filename):
                            path = APP_PATH + '/frame_container/' + filename
                            image = cv2.imread(path, 0)
                            initTransmission = datetime.datetime.now() + datetime.timedelta(hours=1)
                            initTransmission = initTransmission.strftime('%H:%M:%S.%f')[:-2]

                            str_parameters =  f'Init Transmission: {initTransmission}'
                            cv2.putText(image, str_parameters, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                            
                            self.homeModel.saveImagen(image)
                            imageToEncode = self.homeModel.encodeImage(image, encode_param)
                            size = len(imageToEncode)
                            clientSocket.sendall(struct.pack(">L", size) + imageToEncode)
                            
                        else:
                            raise ValueError('index error') 

                    os.remove(APP_PATH + '/frame_container/' + filename)
                    
        clientSocket.close()
            

    """
        @description Method that will allow the user to interact with the system
    """
    def executeThreads(self):

        threads = []

        #cam = Thread(target=self.handlerCAMOpenCV, args=())
        cam = Thread(target=self.handlerVideoOpenCV, args=())
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