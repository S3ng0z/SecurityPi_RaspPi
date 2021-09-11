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
import collections

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
            #aux = Connection()
            #socket = aux.connect()
            #conn = socket.makefile('wb')
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
                        stream = io.BytesIO()
                        for frame in camera.capture_continuous(stream, 'jpeg'):
                            if(lproxy.get('killAll') == 0):
                                break
                            else:
                                
                                # Construct a numpy array from the stream
                                data = np.fromstring(stream.getvalue(), dtype=np.uint8)
                                # "Decode" the image from the array, preserving colour
                                image = cv2.imdecode(data, 1)
                                imS = cv2.resize(image, (960, 540))                # Resize image
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

                                self.visualize_boxes_and_labels_on_image_array(imS,
                                                                            np.squeeze(boxes),
                                                                            np.squeeze(classes).astype(np.int32),
                                                                            np.squeeze(scores),
                                                                            use_normalized_coordinates=True,
                                                                            line_thickness=8)

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

            finally:
                #conn.close()
                #Connection.closeConn(socket)
                gc.collect()
        pass
  
    def workerReviewScreenshots(self, lproxy):
        sys.stdin = open(0)
        try:
            lproxy['killAll'] = int(input())
            
        except EOFError as e:
            print(e)
    
    def visualize_boxes_and_labels_on_image_array(self, image,
                                              boxes,
                                              classes,
                                              scores,
                                              instance_masks=None,
                                              keypoints=None,
                                              use_normalized_coordinates=False,
                                              max_boxes_to_draw=20,
                                              min_score_thresh=.5,
                                              agnostic_mode=False,
                                              line_thickness=4):
        box_to_display_str_map = collections.defaultdict(list)
        box_to_color_map = collections.defaultdict(str)
        box_to_instance_masks_map = {}
        box_to_keypoints_map = collections.defaultdict(list)
        if not max_boxes_to_draw:
            max_boxes_to_draw = boxes.shape[0]
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            if scores is None or scores[i] > min_score_thresh:
                box = tuple(boxes[i].tolist())
                if instance_masks is not None:
                    box_to_instance_masks_map[box] = instance_masks[i]
                if keypoints is not None:
                    box_to_keypoints_map[box].extend(keypoints[i])
                if scores is None:
                    box_to_color_map[box] = 'black'
                else:
                    if agnostic_mode:
                        box_to_color_map[box] = 'DarkOrange'
                    else:
                        box_to_color_map[box] = STANDARD_COLORS[
                            classes[i] % len(STANDARD_COLORS)]

            # Draw all boxes onto image.
        for box, color in box_to_color_map.items():
            ymin, xmin, ymax, xmax = box
            print('-->'+str('***', box, ' ',color))
            print('')
            print('-->' +str(box_to_display_str_map[box]))
            print('')