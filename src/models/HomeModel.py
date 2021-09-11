from datetime import datetime, date
from config import APP_PATH
import os
import time
import io
import struct
import sys
import picamera
from .Connection import Connection
import cv2
import numpy as np
import gc
import tempfile
import tensorflow as tf
import six.moves.urllib as urllib

#import git

path = ''
MODEL_NAME = './ssd_mobilenet_v1_coco_2018_01_28'
MODEL_FILE = MODEL_NAME + '.tar.gz'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'person_label_map.pbtxt'
NUM_CLASSES = 90

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

                camera = picamera.PiCamera()
                camera.vflip = True
                camera.resolution = (1280, 720)
                # Start a preview and let the camera warm up for 2 seconds
                camera.start_preview()
                time.sleep(2)
                detection_graph = tf.Graph()
                with detection_graph.as_default():
                    od_graph_def = tf.GraphDef()
                    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                        serialized_graph = fid.read()
                        od_graph_def.ParseFromString(serialized_graph)
                        tf.import_graph_def(od_graph_def, name='')


                # some helper code
                def load_image_into_numpy_array(image):
                    (im_width, im_height) = image.size
                    return np.array(image.getdata()).reshape(
                        (im_height, im_width, 3)).astype(np.uint8)
                
                # Size, in inches, of the output images.
                IMAGE_SIZE = (12, 8)
                i = 0
                success = True
                #detection of video
                with detection_graph.as_default():
                    with tf.Session(graph=detection_graph) as sess:
                        print('Holaaaaa')
                
                print('Hola Mundo')
                sys.exit("Marks is less than 20")

                stream = io.BytesIO()
                for frame in camera.capture_continuous(stream, 'jpeg'):
                    if(lproxy.get('killAll') == 0):
                        break
                    else:
                        temp_name = next(tempfile._get_candidate_names()) + '.jpg'
                        # Construct a numpy array from the stream
                        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                        # "Decode" the image from the array, preserving colour
                        image = cv2.imdecode(data, 1)
                        imS = cv2.resize(image, (960, 540))                # Resize image
                        #cv2.imwrite(temp_name, imS)

                        conn.write(struct.pack('<L', stream.tell()))
                        conn.flush()
                        
                        stream.seek(0)
                        conn.write(stream.read())
                        
                        stream.seek(0)
                        stream.truncate()
                        if cv2.waitKey(1) == ord('q'):
                            print('Paso por aquí')
                            break
                
                # Write a length of zero to the stream to signal we're done
                conn.write(struct.pack('<L', 0))

            finally:
                conn.close()
                Connection.closeConn(socket)
                gc.collect()
        pass
  
    def workerReviewScreenshots(self, lproxy):
        sys.stdin = open(0)
        try:
            lproxy['killAll'] = int(input())
            
        except EOFError as e:
            print(e)
        