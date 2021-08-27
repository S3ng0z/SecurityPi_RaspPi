from datetime import datetime, date
from config import APP_PATH
import importlib
import os
import time
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
        # printing process id
        #print("ID of process running worker1: {}".format(os.getpid()))
        print("Hola")
        print(lproxy)
        print("killAll = ", lproxy.get('killAll'))
        lproxy.set("killAll", 5)
  
    def workerReviewScreenshots(self, lproxy):
        # printing process id
        #print("ID of process running worker2: {}".format(os.getpid()))
        time.sleep(10)
        print("Mundo")
        print(lproxy)
        print("killAll = ", lproxy.get('killAll'))