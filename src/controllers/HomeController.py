# -*- encoding:utf-8 -*-
from core.Controller import Controller
import gc
import os
import multiprocessing



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
        # printing main program process id
        print("ID of main process: {}".format(os.getpid()))
        # creating processes
        p1 = multiprocessing.Process(target=self.homeModel.worker1())
        p2 = multiprocessing.Process(target=self.homeModel.worker2())
    
        # starting processes
        p1.start()
        p2.start()
    
        # process IDs
        print("ID of process p1: {}".format(p1.pid))
        print("ID of process p2: {}".format(p2.pid))
    
        # wait until processes are finished
        p1.join()
        p2.join()
    
        # both processes finished
        print("Both processes finished execution!")
    
        # check if processes are alive
        print("Process p1 is alive: {}".format(p1.is_alive()))
        print("Process p2 is alive: {}".format(p2.is_alive()))
        #self.homeView.main()
         #opc = input('Enter a option: ')
        #while(self.checkOption(int(input('Enter a option: '))) != 0):
            #self.homeView.main()
        gc.collect()

    def checkOption(self, option):
        option = self.options(option)
        if(option == 'INVALID OPTION'):
            self.homeView.invalidOption()
        elif(option == 0):
            return 0
        self.homeModel.log(option)
        return 1
    
    def options(self, argument):
        default = 'INVALID OPTION'
        return getattr(self, 'opc'+str(argument), lambda:default)()

    def opc0(self):
        return 0

    def opc1(self):
        #return self.homeModel.loadExtractPersons('ExtractPersons').execute()
        pass

    def opc2(self):
        #return self.homeModel.loadRecognizer('Recognizer').execute()
        pass

    def opc3(self):
        #return self.homeModel.loadDetectPersons('DetectPersons').execute()
        pass