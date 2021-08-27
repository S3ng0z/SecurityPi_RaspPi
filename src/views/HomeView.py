from pyfiglet import Figlet
from views.View import View

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
    
    Author: Andrés Gómez
    Versión 1.0
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
        @description Displays the application welcome
        @author Andrés Gómez
    """
    def welcome(self):
        print(TEXT.renderText('Security Pi'))

    """
        @description Method to display the aplication options menu.
        @author Andrés Gómez
    """
    def options(self):
        print('1-. Process video')
        print('2-. Recognizer')
        print('0-. Exit')

    """
        @description Method shows that an option is invalid.
        @author Andrés Gómez
    """
    def invalidOption(self):
        print(Color.YELLOW, 'Option not valid, try again!', Color.END)

    """
        @description Method shows an option request
    """
    def optionRequest(self):
        print('Enter a option: ')

    """
    @Overrite
    """
    def main(self):
        self.options()

    """
    @Overrite
    """
    def close(self):
        print(TEXT.renderText('See you again!'))

    def loadingUpdates(selft):
        print('\n-------------------------------')
        print(Color.YELLOW, 'Do not turn off the power while the system is upgrading!', Color.END)
        print('-------------------------------\n')
        
    
    def completedUpgrades(self):
        print('\n-------------------------------')
        print(Color.GREEN, 'Upgraded system!', Color.END)
        print('-------------------------------\n')
        