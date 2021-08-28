# -*- encoding:utf-8 -*-
from core.Controller import Controller
import gc
import os
import multiprocessing
from multiprocessing import Manager, Value
import time



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
        @Override
    """
    def main(self):
        self.homeModel.log('INIT SESSION')
        self.homeModel.log('INIT Update System')
        #self.homeView.loadingUpdates()
        self.homeModel.loadUpdates()
        #self.homeView.completedUpgrades()
        self.homeModel.log('END Update System')
        #self.homeView.welcome()
        self.mainloop()
        self.homeModel.log('END SESSION')
        #self.homeView.close()

    """
        @description Method that will allow the user to interact with the system
        @author Andrés Gómez
    """
    def mainloop(self):
        processes = []
        with Manager() as manager:
            # creating a list in server process memory
            #parameters = manager.list([('killAll', 1)])
            #lproxy = manager.list()
            #lproxy.append({'killAll':0})
            x = manager.Value('i', 0)
            y = Value('i', 0)

            # printing main program process id
            print("ID of main process: {}".format(os.getpid()))
            # creating processes
            cam = multiprocessing.Process(target=self.homeModel.workerCAM, args=(x, 'x'))
            processes.append(cam)

            reviewScreenshots = multiprocessing.Process(target=self.homeModel.workerReviewScreenshots, args=(y, 'y'))
            processes.append(reviewScreenshots)

            # starting processes
            for process in processes:
                process.start()

            print ('Before waiting: ')
            print ('x = {0}'.format(x.value))
            print ('y = {0}'.format(y.value))

            time.sleep(5.0)
            print ('After waiting: ')
            print ('x = {0}'.format(x.value))
            print ('y = {0}'.format(y.value))
        
            # wait until processes are finished
            for process in processes:
                process.join()

            #print(lproxy)
            
            gc.collect()