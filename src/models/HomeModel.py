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
from models.Configs import *
from models.yolov4 import *

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
                yolo = self.loadYoloModel()
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
                        try:
                            original_image = cv2.cvtColor(imS, cv2.COLOR_BGR2RGB)
                            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                        except:
                            break
                        
                        image_data = self.imagePreprocess(np.copy(original_image), [416, 416])
                        image_data = image_data[np.newaxis, ...].astype(np.float32)

                        pred_bbox = yolo.predict(image_data)

                        pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
                        pred_bbox = tf.concat(pred_bbox, axis=0)

                        bboxes = self.postprocess_boxes(pred_bbox, original_image, 416, 0.5)
                        bboxes = self.nms(bboxes, 0.55, method='nms')

                        print('por aqui: ', bboxes)
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
        
    def imagePreprocess(self, image, target_size, gt_boxes=None):
        ih, iw    = target_size
        h,  w, _  = image.shape

        scale = min(iw/w, ih/h)
        nw, nh  = int(scale * w), int(scale * h)
        image_resized = cv2.resize(image, (nw, nh))

        image_paded = np.full(shape=[ih, iw, 3], fill_value=128.0)
        dw, dh = (iw - nw) // 2, (ih-nh) // 2
        image_paded[dh:nh+dh, dw:nw+dw, :] = image_resized
        image_paded = image_paded / 255.

        if gt_boxes is None:
            return image_paded

        else:
            gt_boxes[:, [0, 2]] = gt_boxes[:, [0, 2]] * scale + dw
            gt_boxes[:, [1, 3]] = gt_boxes[:, [1, 3]] * scale + dh
            return image_paded, gt_boxes

    def loadYoloModel(self):
            
        if YOLO_FRAMEWORK == "tf": # TensorFlow detection
            if YOLO_TYPE == "yolov4":
                #Darknet_weights = YOLO_V4_TINY_WEIGHTS if TRAIN_YOLO_TINY else YOLO_V4_WEIGHTS
                Darknet_weights = YOLO_V4_TINY_WEIGHTS
                
            #print(Darknet_weights)    
            if YOLO_CUSTOM_WEIGHTS == False:
                #print("Loading Darknet_weights from:", Darknet_weights)
                yolo = Create_Yolo(input_size=YOLO_INPUT_SIZE, CLASSES=YOLO_COCO_CLASSES)
                self.loadYoloWeights(yolo, Darknet_weights) # use Darknet weights

        return yolo

    def loadYoloWeights(self, model, weights_file):
        tf.keras.backend.clear_session() # used to reset layer names
        # load Darknet original weights to TensorFlow model

        if YOLO_TYPE == "yolov4":
            range1 = 110 if not TRAIN_YOLO_TINY else 21
            range2 = [93, 101, 109] if not TRAIN_YOLO_TINY else [17, 20]
        
        with open(weights_file, 'rb') as wf:
            major, minor, revision, seen, _ = np.fromfile(wf, dtype=np.int32, count=5)

            j = 0
            for i in range(range1):
                if i > 0:
                    conv_layer_name = 'conv2d_%d' %i
                else:
                    conv_layer_name = 'conv2d'
                    
                if j > 0:
                    bn_layer_name = 'batch_normalization_%d' %j
                else:
                    bn_layer_name = 'batch_normalization'
                
                conv_layer = model.get_layer(conv_layer_name)
                filters = conv_layer.filters
                k_size = conv_layer.kernel_size[0]
                in_dim = conv_layer.input_shape[-1]

                if i not in range2:
                    # darknet weights: [beta, gamma, mean, variance]
                    bn_weights = np.fromfile(wf, dtype=np.float32, count=4 * filters)
                    # tf weights: [gamma, beta, mean, variance]
                    bn_weights = bn_weights.reshape((4, filters))[[1, 0, 2, 3]]
                    bn_layer = model.get_layer(bn_layer_name)
                    j += 1
                else:
                    conv_bias = np.fromfile(wf, dtype=np.float32, count=filters)

                # darknet shape (out_dim, in_dim, height, width)
                conv_shape = (filters, in_dim, k_size, k_size)
                conv_weights = np.fromfile(wf, dtype=np.float32, count=np.product(conv_shape))
                # tf shape (height, width, in_dim, out_dim)
                conv_weights = conv_weights.reshape(conv_shape).transpose([2, 3, 1, 0])

                if i not in range2:
                    conv_layer.set_weights([conv_weights])
                    bn_layer.set_weights(bn_weights)
                else:
                    conv_layer.set_weights([conv_weights, conv_bias])

            assert len(wf.read()) == 0, 'failed to read all data'

    def postprocess_boxes(self, pred_bbox, original_image, input_size, score_threshold):
        valid_scale=[0, np.inf]
        pred_bbox = np.array(pred_bbox)

        pred_xywh = pred_bbox[:, 0:4]
        pred_conf = pred_bbox[:, 4]
        pred_prob = pred_bbox[:, 5:]

        # 1. (x, y, w, h) --> (xmin, ymin, xmax, ymax)
        pred_coor = np.concatenate([pred_xywh[:, :2] - pred_xywh[:, 2:] * 0.5,
                                    pred_xywh[:, :2] + pred_xywh[:, 2:] * 0.5], axis=-1)
        # 2. (xmin, ymin, xmax, ymax) -> (xmin_org, ymin_org, xmax_org, ymax_org)
        org_h, org_w = original_image.shape[:2]
        resize_ratio = min(input_size / org_w, input_size / org_h)

        dw = (input_size - resize_ratio * org_w) / 2
        dh = (input_size - resize_ratio * org_h) / 2

        pred_coor[:, 0::2] = 1.0 * (pred_coor[:, 0::2] - dw) / resize_ratio
        pred_coor[:, 1::2] = 1.0 * (pred_coor[:, 1::2] - dh) / resize_ratio

        # 3. clip some boxes those are out of range
        pred_coor = np.concatenate([np.maximum(pred_coor[:, :2], [0, 0]),
                                    np.minimum(pred_coor[:, 2:], [org_w - 1, org_h - 1])], axis=-1)
        invalid_mask = np.logical_or((pred_coor[:, 0] > pred_coor[:, 2]), (pred_coor[:, 1] > pred_coor[:, 3]))
        pred_coor[invalid_mask] = 0

        # 4. discard some invalid boxes
        bboxes_scale = np.sqrt(np.multiply.reduce(pred_coor[:, 2:4] - pred_coor[:, 0:2], axis=-1))
        scale_mask = np.logical_and((valid_scale[0] < bboxes_scale), (bboxes_scale < valid_scale[1]))

        # 5. discard boxes with low scores
        classes = np.argmax(pred_prob, axis=-1)
        scores = pred_conf * pred_prob[np.arange(len(pred_coor)), classes]
        score_mask = scores > score_threshold
        mask = np.logical_and(scale_mask, score_mask)
        coors, scores, classes = pred_coor[mask], scores[mask], classes[mask]

        return np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1)

    def nms(self, bboxes, iou_threshold, sigma=0.3, method='nms'):
        
        classes_in_img = list(set(bboxes[:, 5]))
        best_bboxes = []

        for cls in classes_in_img:
            cls_mask = (bboxes[:, 5] == cls)
            cls_bboxes = bboxes[cls_mask]
            # Process 1: Determine whether the number of bounding boxes is greater than 0 
            while len(cls_bboxes) > 0:
                # Process 2: Select the bounding box with the highest score according to socre order A
                max_ind = np.argmax(cls_bboxes[:, 4])
                best_bbox = cls_bboxes[max_ind]
                best_bboxes.append(best_bbox)
                cls_bboxes = np.concatenate([cls_bboxes[: max_ind], cls_bboxes[max_ind + 1:]])
                # Process 3: Calculate this bounding box A and
                # Remain all iou of the bounding box and remove those bounding boxes whose iou value is higher than the threshold 
                iou = self.bboxes_iou(best_bbox[np.newaxis, :4], cls_bboxes[:, :4])
                weight = np.ones((len(iou),), dtype=np.float32)

                assert method in ['nms', 'soft-nms']

                if method == 'nms':
                    iou_mask = iou > iou_threshold
                    weight[iou_mask] = 0.0

                if method == 'soft-nms':
                    weight = np.exp(-(1.0 * iou ** 2 / sigma))

                cls_bboxes[:, 4] = cls_bboxes[:, 4] * weight
                score_mask = cls_bboxes[:, 4] > 0.
                cls_bboxes = cls_bboxes[score_mask]

        return best_bboxes

    def bboxes_iou(self, boxes1, boxes2):
        boxes1 = np.array(boxes1)
        boxes2 = np.array(boxes2)

        boxes1_area = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
        boxes2_area = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])

        left_up       = np.maximum(boxes1[..., :2], boxes2[..., :2])
        right_down    = np.minimum(boxes1[..., 2:], boxes2[..., 2:])

        inter_section = np.maximum(right_down - left_up, 0.0)
        inter_area    = inter_section[..., 0] * inter_section[..., 1]
        union_area    = boxes1_area + boxes2_area - inter_area
        ious          = np.maximum(1.0 * inter_area / union_area, np.finfo(np.float32).eps)

        return ious