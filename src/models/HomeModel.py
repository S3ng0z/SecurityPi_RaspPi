from datetime import datetime, date
from config import APP_PATH
import os
import time
import io
import struct
import sys
from models.singlemotiondetector import SingleMotionDetector
from picamera.array import PiRGBArray
import picamera
from .Connection import Connection
import cv2
import numpy as np
import gc
import tempfile
import tensorflow as tf
import six.moves.urllib as urllib
import collections
import imutils
from imutils.video import VideoStream
import pickle
import socket
#import git

path = ''
MODEL_NAME = './ssd_mobilenet_v1_coco_2018_01_28'
MODEL_FILE = MODEL_NAME + '.tar.gz'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'person_label_map.pbtxt'
NUM_CLASSES = 90
STANDARD_COLORS = [
    'AliceBlue', 'Chartreuse', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque',
    'BlanchedAlmond', 'BlueViolet', 'BurlyWood', 'CadetBlue', 'AntiqueWhite',
    'Chocolate', 'Coral', 'CornflowerBlue', 'Cornsilk', 'Crimson', 'Cyan',
    'DarkCyan', 'DarkGoldenRod', 'DarkGrey', 'DarkKhaki', 'DarkOrange',
    'DarkOrchid', 'DarkSalmon', 'DarkSeaGreen', 'DarkTurquoise', 'DarkViolet',
    'DeepPink', 'DeepSkyBlue', 'DodgerBlue', 'FireBrick', 'FloralWhite',
    'ForestGreen', 'Fuchsia', 'Gainsboro', 'GhostWhite', 'Gold', 'GoldenRod',
    'Salmon', 'Tan', 'HoneyDew', 'HotPink', 'IndianRed', 'Ivory', 'Khaki',
    'Lavender', 'LavenderBlush', 'LawnGreen', 'LemonChiffon', 'LightBlue',
    'LightCoral', 'LightCyan', 'LightGoldenRodYellow', 'LightGray', 'LightGrey',
    'LightGreen', 'LightPink', 'LightSalmon', 'LightSeaGreen', 'LightSkyBlue',
    'LightSlateGray', 'LightSlateGrey', 'LightSteelBlue', 'LightYellow', 'Lime',
    'LimeGreen', 'Linen', 'Magenta', 'MediumAquaMarine', 'MediumOrchid',
    'MediumPurple', 'MediumSeaGreen', 'MediumSlateBlue', 'MediumSpringGreen',
    'MediumTurquoise', 'MediumVioletRed', 'MintCream', 'MistyRose', 'Moccasin',
    'NavajoWhite', 'OldLace', 'Olive', 'OliveDrab', 'Orange', 'OrangeRed',
    'Orchid', 'PaleGoldenRod', 'PaleGreen', 'PaleTurquoise', 'PaleVioletRed',
    'PapayaWhip', 'PeachPuff', 'Peru', 'Pink', 'Plum', 'PowderBlue', 'Purple',
    'Red', 'RosyBrown', 'RoyalBlue', 'SaddleBrown', 'Green', 'SandyBrown',
    'SeaGreen', 'SeaShell', 'Sienna', 'Silver', 'SkyBlue', 'SlateBlue',
    'SlateGray', 'SlateGrey', 'Snow', 'SpringGreen', 'SteelBlue', 'GreenYellow',
    'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White',
    'WhiteSmoke', 'Yellow', 'YellowGreen'
]

"""
    Model description
"""
class HomeModel:
    
    def __init__(self, controller):
        self.homeController = controller
        pass
    """
        @description This method is called when the application is opened and its purpose is to open a text file where the history of the application execution will be stored.
    """
    def openLogging(self):
        global path
        
        today = date.today()
        filename = 'logging_'+str(today)+'.txt'
        if not os.path.exists(APP_PATH+"/logs"):
            os.makedirs(APP_PATH+"/logs")
        
        path = os.path.join(APP_PATH + "/logs/", filename)
        open(path, 'a+')

    """
        @description Method that writes into the history file a row of information about an action on the application.
    """
    def log(self, info):
        global path
        
        file = open(path, 'a+')
        now = datetime.now()
        line = str(info) + ' - ' + str(now) + '\n'
        
        file.write(line)
        file.close()

    
    """
        @description Method used to update the system. Used each time the application is initialised.
    """
    def loadUpdates(self):
        os.system('../scripts/executeUpdates.sh')

    def clearCache(self):
        pass

    """
        @description Method that establishes socket connection.
    """
    def connectSocket(self):
        return Connection.connect()

    """
        @description Method that establishes socket connection.
    """
    def connectSocketSendScreenShoot(self):
        return Connection.connectSendScreenShoot()
    
    """
        @description Method that activates the camera for the use of the application.
    """
    def connectCamera(self):
        camera = picamera.PiCamera()
        camera.vflip = True
        camera.resolution = (1280, 720)
        return camera

    """
        @description Method that activates the camera for the use of the application.
    """
    def openVideo(self):
        return cv2.VideoCapture('../test/test-480p.mp4')

    def processImage(self, image, faceCascade):
        
        #grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        facesContainer = faceCascade.detectMultiScale(
            image, scaleFactor=1.1, minNeighbors=15, minSize=(50, 50))

        if len(facesContainer) != 0:
            for(x, y, w, h) in facesContainer:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            if not os.path.isdir(APP_PATH+'/frame_container'):
                os.mkdir(APP_PATH+'/frame_container')
            
            tempName = next(tempfile._get_candidate_names())
            image = cv2.resize(image, (640, 480))
            cv2.imwrite((APP_PATH+'/frame_container/'+str(tempName)+'.jpg'), image)
        
        return image
    
    def encodeImage(self, image, encode_param):
        result, frame = cv2.imencode('.jpg', image, encode_param)
        data = pickle.dumps(frame, 0)
        return data

    def getPathToCKPT(self):
        return PATH_TO_CKPT
    
    def processImagenTF(self, detection_graph, imS, sess):
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(imS, axis=0)
        # Extract image tensor
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = detection_graph.get_tensor_by_name('detection_scores:0')
        classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        # Actual detection.
        (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections], feed_dict={image_tensor: image_np_expanded})
        
        if(num_detections > 0):
            print('num_detections ', num_detections)

        return imS

    def workerCAM(self, lproxy):

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('192.168.228.31', 8000))
        connection = client_socket.makefile('wb')
        print('@@Test' + APP_PATH)
        pathHaarcascade = APP_PATH + '/lib/haarcascade_frontalface_default.xml'
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)

        #cam = cv2.VideoCapture(0)
        #cam = cv2.VideoCapture(-1, cv2.CAP_V4L)

        #cam.set(3, 720);
        #cam.set(4, 720);
        
        # initialize the camera and grab a reference to the raw camera capture
        camera = picamera.PiCamera()
        camera.vflip = True
        camera.resolution = (720, 680)
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(2)
        # allow the camera to warmup
        time.sleep(0.1)

        img_counter = 0

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        detection_graph = tf.Graph()
        total = 0
        
        with detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
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
                    grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    facesContainer = faceCascade.detectMultiScale(
                        grayScale, scaleFactor=1.1, minNeighbors=15, minSize=(70, 70))
                    for(x, y, w, h) in facesContainer:
                        cv2.rectangle(grayScale, (x, y),
                                      (x + w, y + h), (0, 255, 0), 2)
                    '''
                    if total % 5 == 0:
                        total = 0;
                        image_np_expanded = np.expand_dims(imS, axis=0)
                        image_tensor = detection_graph.get_tensor_by_name(
                            'image_tensor:0')
                        # Each box represents a part of the image where a particular object was detected.
                        boxes = detection_graph.get_tensor_by_name(
                                'detection_boxes:0')
                            # Each score represent how level of confidence for each of the objects.
                            # Score is shown on the result image, together with the class label.
                        scores = detection_graph.get_tensor_by_name(
                                'detection_scores:0')
                        classes = detection_graph.get_tensor_by_name(
                                'detection_classes:0')
                        num_detections = detection_graph.get_tensor_by_name(
                                'num_detections:0')
                            # Actual detection.
                        (boxes, scores, classes, num_detections) = sess.run(
                                    [boxes, scores, classes, num_detections],
                                    feed_dict={image_tensor: image_np_expanded})
                        if(num_detections > 0):
                            print('num_detections ', num_detections)
                    
                    total += 1
                    '''
                    result, frame = cv2.imencode(
                        '.jpg', grayScale, encode_param)
                    #data = zlib.compress(pickle.dumps(frame, 0))
                    data = pickle.dumps(frame, 0)
                    size = len(data)
                    stream.seek(0)
                    stream.truncate()
                    #print("{}: {}".format(img_counter, size))
                    client_socket.sendall(struct.pack(">L", size) + data)
                    img_counter += 1

        cam.release()
        pass
  
    def workerReviewScreenshots(self, lproxy):
        pathHaarcascade = APP_PATH + '/libs/haarcascade_frontalface_alt2.xml';
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)
        if not os.path.isdir(APP_PATH+'/store'):
            os.mkdir(APP_PATH+'/store')
        
        if not os.path.isdir(APP_PATH+'/sender'):
            os.mkdir(APP_PATH+'/sender')
        
        while lproxy.get('killAll') != 0:
            path, dirs, files = next(os.walk(APP_PATH+'/store'))
            file_count = len(files)
            if(file_count > 0):
                for filename in os.listdir('./store'):
                    if filename.endswith(".jpg") or filename.endswith(".png"):
                        image = cv2.imread(os.path.join('./store', filename))
                        grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        facesContainer = faceCascade.detectMultiScale(grayScale, scaleFactor = 1.1, minNeighbors = 15, minSize = (70, 70))
                        for(x, y, w, h) in facesContainer:
                            cv2.rectangle(grayScale, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            roiColor = cv2.resize(grayScale[y:(y + h), x:(x + h)], (w, h), interpolation = cv2.INTER_AREA)
                            if not os.path.isdir(APP_PATH+'/store/facesContainer'):
                                os.mkdir(APP_PATH+'/store/facesContainer')
                            
                            tempName = next(tempfile._get_candidate_names())
                            img = cv2.GaussianBlur(roiColor, (3,3), 0)
                            
                            #self.homeModel.log('[INFO] ' + tempName + ' only GB: ' + str(img) + ' GB+LP: ' + str(self.varianceLaplacian(img)) + ' LP: ' + str(self.varianceLaplacian(roiColor)))
                            print('[INFO] ' + tempName + ' LP: ' + str(self.varianceLaplacian(img)) + ' LP: ' + str(self.varianceLaplacian(roiColor)))
                            cv2.imwrite((APP_PATH+'/store/facesContainer/'+str(tempName)+'.jpg'), roiColor)
                    cv2.imwrite((APP_PATH+'/sender/'+str(filename)+'.jpg'), image)
                    os.remove(os.path.join('./store', filename))


    def workerSendScreenshots(self, lproxy):
        if not os.path.isdir(APP_PATH+'/frame_container'):
            os.mkdir(APP_PATH+'/frame_container')

        path, dirs, files = next(os.walk(APP_PATH+'/frame_container'))
        file_count = len(files)
        if(file_count > 0):
            for filename in os.listdir('./frame_container'):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    print('Hola Mundo')
