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
        if(lproxy.get('killAll') != 0):
            aux = Connection()
            socket = aux.connect()
            conn = socket.makefile('wb')
            try:
                temp_name = next(tempfile._get_candidate_names())
                #camera = picamera.PiCamera()
                camera = VideoStream(usePiCamera=1).start()
                #camera.vflip = True
                #camera.resolution = (1280, 720)
                #camera.resolution = (1280, 720)
                # Start a preview and let the camera warm up for 2 seconds
                #camera.start_preview()
                time.sleep(2)
                '''
                detection_graph = tf.Graph()
                contFrames = 0
                with detection_graph.as_default():
                    od_graph_def = tf.GraphDef()
                    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                        serialized_graph = fid.read()
                        od_graph_def.ParseFromString(serialized_graph)
                        tf.import_graph_def(od_graph_def, name='')
                '''
                #detection of video
                '''
                with detection_graph.as_default():
                    with tf.Session(graph=detection_graph) as sess'''
                stream = io.BytesIO()
                #rawCapture = PiRGBArray(camera, size=(640, 480))
                md = SingleMotionDetector(accumWeight=0.1)
                total = 0
                #for frame in camera.capture_continuous(stream, 'jpeg'):
                #for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                while True:
                    if(lproxy.get('killAll') == 0):
                        break
                    else:
                        #data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                        #image = cv2.imdecode(data, 1)
                        frame = camera.read()
                        frame = imutils.resize(frame, width=720)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        gray = cv2.GaussianBlur(gray, (7, 7), 0)
                        # grab the current timestamp and draw it on the frame
                        img_str = cv2.imencode('.jpg', frame)[1].tostring()
                        timestamp = datetime.now()
                        cv2.putText(frame, timestamp.strftime(
                            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                        # update the background model and increment the total number
                        # of frames read thus far
                        md.update(gray)
                        if(total%10 == 0):
                            # detect motion in the image
                            motion = md.detect(gray)

                            # cehck to see if motion was found in the frame
                            if motion is not None:
                                # unpack the tuple and draw the box surrounding the
                                # "motion area" on the output frame
                                (thresh, (minX, minY, maxX, maxY)) = motion
                                cv2.rectangle(frame, (minX, minY), (maxX, maxY),
                                                    (0, 0, 255), 2)
                            
                        
                        total += 1

                        # clear the stream in preparation for the next frame
                        #rawCapture.truncate(0)
                        #stream.seek(0)
                        #conn.write(stream.read())
                        #conn.write(struct.pack('<L', stream.tell()))
                        conn.flush()
                        conn.write(img_str)
                        if cv2.waitKey(1) == ord('q'):
                            print('Paso por aquí')
                            break
                        
                        '''
                        conn.write(struct.pack('<L', stream.tell()))
                        conn.flush()

                        stream.seek(0)
                        conn.write(stream.read())

                        stream.seek(0)
                        stream.truncate()
                        if cv2.waitKey(1) == ord('q'):
                            print('Paso por aquí')
                            break
                        '''
                        # Write a length of zero to the stream to signal we're done
                        #conn.write(struct.pack('<L', 0))
                        
                        
                        '''
                        temp_name = next(tempfile._get_candidate_names()) + '.jpg'
                        # Construct a numpy array from the stream
                        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                        # "Decode" the image from the array, preserving colour
                        image = cv2.imdecode(data, 1)
                        imS = cv2.resize(image, (1280, 720)) # Resize image
                        #cv2.imwrite(temp_name, imS)
                        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                        image_np_expanded = np.expand_dims(imS, axis=0)
                        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                        # Each box represents a part of the image where a particular object was detected.
                        boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                        # Each score represent how level of confidence for each of the objects.
                        # Score is shown on the result image, together with the class label.
                        scores = detection_graph.get_tensor_by_name('detection_scores:0')
                        classes = detection_graph.get_tensor_by_name('detection_classes:0')
                        num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                        # Actual detection.
                        (boxes, scores, classes, num_detections) = sess.run(
                            [boxes, scores, classes, num_detections],
                            feed_dict={image_tensor: image_np_expanded})
                        if(num_detections > 0):
                            print('num_detections ', num_detections)
                            if not os.path.isdir(APP_PATH+'/store'):
                                os.mkdir(APP_PATH+'/store')
                            cv2.imwrite((APP_PATH+'/store/'+temp_name), imS)
                            
                        #conn.write(struct.pack('<L', stream.tell()))
                        #conn.flush()
                        
                        stream.seek(0)
                        #conn.write(stream.read())
                        
                        stream.seek(0)
                        stream.truncate()
                        if cv2.waitKey(1) == ord('q'):
                            print('Paso por aquí')
                            break
                
                        # Write a length of zero to the stream to signal we're done
                        #conn.write(struct.pack('<L', 0))
                        '''
            finally:
                conn.close()
                aux.closeConn(socket)
                gc.collect()
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
        pathHaarcascade = APP_PATH + '/libs/haarcascade_frontalface_alt2.xml';
        faceCascade = cv2.CascadeClassifier(pathHaarcascade)
        if not os.path.isdir(APP_PATH+'/store'):
            os.mkdir(APP_PATH+'/store')
        
        while lproxy.get('killAll') != 0:
            path, dirs, files = next(os.walk(APP_PATH+'/store'))
            file_count = len(files)
            if(file_count > 0):
                for filename in os.listdir('./store'):
                    if filename.endswith(".jpg") or filename.endswith(".png"):
                        print('Hola Mundo')
