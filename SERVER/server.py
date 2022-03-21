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

HOST = '192.168.0.75'  # Standard loopback interface address (localhost)
#HOST = '192.168.0.75'
PORT = 8000        # Port to listen on (non-privileged ports are > 1023)
PORT2 = 8080

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def setup(self):
        print('Accept connection from {}'.format(self.client_address))

    def handle(self):
        if not os.path.isdir('./frame_container'):
            os.mkdir('./frame_container')

        while True:
            try:
                # Head size ('24si' = 28 bytes)
                file_head_size = struct.calcsize('24si')
                # Receive file head
                buf = self.request.recv(file_head_size)
                if buf:
                    # Unpack head and get timestamp and file size
                    timestamp, file_size = struct.unpack('24si', buf)
                    timestamp = timestamp.decode('utf-8').strip('\x00')
                    received_size = 0  # Already received file size
                    data = b''
                    '''
                        If file size minus received size greater than 1024,
                            receive 1024 bytes once time,
                        else:
                            receive file size minus received size.
                            (Attention: receive 1024 will stick package.)
                    '''
                    while not received_size == file_size:
                        if file_size - received_size > 1024:
                            data += self.request.recv(1024)
                            received_size += 1024
                        else:
                            data += self.request.recv(file_size - received_size)
                            received_size = file_size
                    # BytesIO: Read bytes data from memory
                    # Then open it with PIL
                    data = BytesIO(data)
                    try:
                        ImageFile.LOAD_TRUNCATED_IMAGES = True
                        with Image.open(data) as f:
                            tempName = next(tempfile._get_candidate_names())
                            frame = f.convert('RGB')
                            print('./frame_container/'+str(tempName)+'.jpg')
                            f.save('./frame_container/'+str(tempName)+'.jpg')
                            #cv2.imwrite('./frame_container/'+str(tempName)+'.jpg', frame)
                            print('Recibido...')
                    except UnidentifiedImageError as uerr:
                        print('Erroraco UnidentifiedImageError: ' + str(uerr))
            except Exception as e:
                a = str(e)
                #print('Exception'+ str(e))

def handlerCam(conn, data, payload_size, img):
    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)

        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))

        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if img is None:
            img = pl.imshow(frame)
        else:
            img.set_data(frame)
        
        pl.pause(0.25)
        #pl.draw()

def recieveScreenShoot(conn, data, payload_size, img):
    
    while True:
        data = b''
        if not os.path.isdir('./frame_container'):
            os.mkdir('./frame_container')
        
        file_head_size = struct.calcsize('24si')

        buf = conn.recv(file_head_size)
        if buf:
            # Unpack head and get timestamp and file size
            timestamp, file_size = struct.unpack('24si', buf)
            timestamp = timestamp.decode('utf-8').strip('\x00')
            received_size = 0  # Already received file size
            data = b''
            while not received_size == file_size:
                if file_size - received_size > 1024:
                    data += conn.recv(1024)
                    received_size += 1024
                else:
                    data += conn.recv(file_size - received_size)
                    received_size = file_size
            # BytesIO: Read bytes data from memory
            # Then open it with PIL
            data = BytesIO(data)
            try:
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                with Image.open(data) as f:
                    tempName = next(tempfile._get_candidate_names())
                    frame = f.convert('RGB')
                    print('./frame_container/'+str(tempName)+'.jpg')
                    f.save('./frame_container/'+str(tempName)+'.jpg')
                    #cv2.imwrite('./frame_container/'+str(tempName)+'.jpg', frame)
                    print('Recibido...')
            except UnidentifiedImageError:
                print('Erroraco')
            
        
        '''

        while len(data) < payload_size:
            data += conn.recv(4096)

        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))
        print('msg_size: ' + str(msg_size) + ' escribiendo...')
        while len(data) < msg_size:
            data += conn.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if not frame is None: 
            tempName = next(tempfile._get_candidate_names())
            print('./frame_container/'+str(tempName)+'.jpg')
            cv2.imwrite('./frame_container/'+str(tempName)+'.jpg', frame)
            print('Recibido...')
        '''
        '''
        dataRecieve = conn.recv(4)
        image_size = int(struct.unpack('>L', dataRecieve)[0])
        print('image_size: ' + str(image_size))
        if image_size != 0:
            tempName = next(tempfile._get_candidate_names())
            file = open('./frame_container/'+str(tempName)+'.jpg', "wb")
            print('./frame_container/'+str(tempName)+'.jpg')
            print('dataRecieve: ' + str(dataRecieve))
    
            data = b""
            while len(data) < image_size:
                data += conn.recv(4096)
                if not data:
                    print('A pasado algo')
                    break
                else:
                    print('len(data): '+str(len(data))+'recibiendo... ')

            if data:
                file.write(data)
                print ("Data Received successfully")
                
            file.close()
        '''
        '''
        fileZip = open('./frame_container/'+str(tempName)+'.zip', "wb")
        nextStep = False
        while True:
            # get file bytes
            data = conn.recv(4096)
            if not data:
                break
            nextStep = True
            # write bytes on file
            fileZip.write(data)
        if nextStep:
            zip = zipfile.ZipFile('./frame_container/'+str(tempName)+'.zip', "r")
            zip.extractall('./frame_container')
        fileZip.close()
        '''
        '''
        filename = conn.recv(1024).decode()

        f = open(filename, 'wb')
        l = conn.recv(1024)
        while(l):
            f.write(l)
            l = conn.recv(1024)
        f.close()
        print('[+] Received file ' + filename)

        with zipfile.ZipFile(filename, 'rb') as file:
            print('[+] Extracting files...')
            file.extractall()
            print('[+] Done')

        os.remove(filename)
        con.close()
        ss.close()
        '''
        '''
        while len(data) < payload_size:
            data += conn.recv(4096)
        
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += conn.recv(4096)

        if not data:
            break
        file.write(data)
        file.close()
    conn.close()
    '''
    '''
    data = conn.recv(4096)  # stream-based protocol
    while len(data) < payload_size:
        data += conn.recv(4096)
    
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)

    if not data:
        break
    
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    file.write(frame)
    file.close()

    print('img: ' + (str(tempName)+'.jpg') + ' received');
    ---
    while len(data) < payload_size:
        data += conn.recv(4096)
    print("Done Recv: {}".format(len(data)))
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    print("msg_size: {}".format(msg_size))

    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    
    if not os.path.isdir('/frame_container'):
        os.mkdir('/frame_container')
    
    tempName = next(tempfile._get_candidate_names())
    cv2.imwrite(('/frame_container/'+str(tempName)+'.jpg'), frame)
    '''


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    data = b""
    payload_size = struct.calcsize(">L")
    img = None

    #with socket.socket() as sst:
    #sst.bind((HOST, PORT2))
    #sst.listen()
    #connSST, addrSST = sst.accept()
    print('Connected by', addr)
    #print('Connected2 by', addrSST)
    #dataSST = b""
    #payload_sizeSST = struct.calcsize(">L")
    #imgSST = None
    
    threads = []

    cam = Thread(target=handlerCam, args=(conn, data, payload_size, img))
    threads.append(cam)

    #recieveScreenShoot = Thread(target=recieveScreenShoot, args=(connSST, dataSST, payload_sizeSST, imgSST))
    #threads.append(recieveScreenShoot)
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.ThreadingTCPServer((HOST, PORT2), ThreadedTCPRequestHandler)
    recieveScreenShoot = Thread(target=server.serve_forever)
    recieveScreenShoot.demon = True
    threads.append(recieveScreenShoot)

    #camTF = Thread(target=self.handlerCAMTensorFlow, args=(killAll,))
    #threads.append(camTF)

    # starting processes
    for thd in threads:
        thd.start()

    # wait until processes are finished
    for thd in threads:#
        thd.join()
    
    gc.collect()
    '''
        while len(data) < payload_size:
            data += conn.recv(4096)

        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        
        if img is None:
            img = pl.imshow(frame)
        else:
            img.set_data(frame)
        

        pl.pause(0.25)
        pl.draw()
    '''