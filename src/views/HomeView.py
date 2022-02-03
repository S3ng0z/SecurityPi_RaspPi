from pyfiglet import Figlet
from views.View import View
import cv2

TEXT = Figlet(font='slant')

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

"""
    View associated with HomeController. It will be responsible for program's 
    main screen view.
"""
class HomeView(View):
    
    #-----------------------------------------------------------------------
    #        Constructor
    #-----------------------------------------------------------------------
    """
        @param controller Controller of this view
    """
    def __init__(self, controller):
        super().__init__()
        self.homeController = controller
        pass
        
    
    #-----------------------------------------------------------------------
    #        Methods
    #-----------------------------------------------------------------------

    """
        @description Draws a box around the faces in the image and displays it on the screen
        @param image - Matrix containing the image where the objects are detected.
        @param faces - Positioning of detected faces rect(x, y, w, h)

    """
    def displayInageDetection(self, image, faces):
        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Display
        cv2.imshow('img', image)


    """
        @description Displays the application welcome
    """
    def welcome(self):
        print(TEXT.renderText('Security Pi'))

    """
        @description Method to display the aplication options menu.
    """
    def options(self):
        print('1-. Recognizer')
        print('0-. Exit')

    """
        @description Method shows that an option is invalid.
    """
    def invalidOption(self):
        print(Color.YELLOW, 'Option not valid, try again!', Color.END)

    """
        @description Method shows an option request
    """
    def optionRequest(self):
        print('Enter a option: ')

    """
        @description Method called by the controller at the start of the application or after finishing a task, which displays a menu with options.
    """
    def main(self):
        self.options()
        self.optionRequest()

    """
        @description Method called when closing the application
    """
    def close(self):
        print(TEXT.renderText('See you again!'))

    """
        @description Method called at the start of the system update.
    """

    def loadingUpdates(selft):
        print('\n-------------------------------')
        print(Color.YELLOW, 'Do not turn off the power while the system is upgrading!', Color.END)
        print('-------------------------------\n')
        
    """
        @descripcion Notifies that the system has been updated.
    """
    def completedUpgrades(self):
        print('\n-------------------------------')
        print(Color.GREEN, 'Upgraded system!', Color.END)
        print('-------------------------------\n')

    """
    @description Method to display the aplication options menu.
    @author Andrés Gómez
    """
    def options(self):
        print('1-. Process video')
        print('2-. Recognizer')
        print('0-. Exit')
        