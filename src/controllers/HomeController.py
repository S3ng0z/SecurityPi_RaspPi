# -*- encoding:utf-8 -*-
from core.Controller import Controller
from models.Connection import Connection
import gc
import os
import io
import struct
import time
import cv2
import numpy as np
import tensorflow as tf
from threading import Thread, Event
import multiprocessing
from multiprocessing import Manager

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
    def handlerCAMOpenCV(self):
        clientSocket = self.homeModel.connectSocket()
        camera = self.homeModel.connectCamera()

        camera.start_preview()
        time.sleep(2)

        stream = io.BytesIO()
        for frame in camera.capture_continuous(stream, 'jpeg'):

            clientSocket.write(struct.pack('<L', stream.tell()))
            clientSocket.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            # Construct a numpy array from the stream
            data = np.fromstring(stream.getvalue(), dtype=np.uint8)
            # "Decode" the image from the array, preserving colour
            image = cv2.imdecode(data, 1)

            imageFaceDetected = self.homeModel.processImage(image)
            imageToEncode = self.homeModel.encodeImage(imageFaceDetected)

            connection.write(imageToEncode)
            
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
            connection.write(struct.pack('<L', 0))
            '''
            size = len(imageToEncode)
            stream.seek(0)
            stream.truncate()
            clientSocket.sendall(struct.pack(">L", size) + imageToEncode)
            '''

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
            

    """
        @description Method that will allow the user to interact with the system
    """
    def executeThreads(self):

        threads = []


        cam = Thread(target=self.handlerCAMOpenCV, args=())
        threads.append(cam)

        #camTF = Thread(target=self.handlerCAMTensorFlow, args=(killAll,))
        #threads.append(camTF)

         # starting processes
        for thd in threads:
            thd.start()
    
        # wait until processes are finished
        for thd in threads:#
            thd.join()
        
        gc.collect()
 

    """
        @description Method that will allow the user to interact with the system
        @author Andrés Gómez
    """
    def loop2(self):
        processes = []
        gc.collect()
        with Manager() as manager:
            # creating a list in server process memory
            #parameters = manager.list([('killAll', 1)])
            #lproxy = manager.list()
            #lproxy.append({'killAll':0})
            lproxy = manager.dict()
            lproxy['killAll'] = 1

            # printing main program process id
            print("ID of main process: {}".format(os.getpid()))
            # creating processes
            '''
            reviewScreenshots = multiprocessing.Process(target=self.homeModel.workerReviewScreenshots, args=(lproxy,))
            processes.append(reviewScreenshots)

            sendScreenShoot = multiprocessing.Process(target=self.homeModel.workerSendScreenshots, args=(lproxy,))
            processes.append(sendScreenShoot)
            '''
            cam = multiprocessing.Process(target=self.homeModel.workerCAM, args=(lproxy,))
            processes.append(cam)

            

            # starting processes
            for process in processes:
                process.start()
        
            # wait until processes are finished
            for process in processes:
                process.join()

            print(lproxy)
            
            gc.collect()