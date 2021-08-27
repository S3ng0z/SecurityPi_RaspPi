import abc

"""
    Responsible for the program interface.
"""
class Model(metaclass=abc.ABCMeta):
    """
        Displays view on screen
    """
    @abc.abstractmethod
    def main(self):
        return

    """
        Closes the interface. It is called when the window is closed.
    """
    @abc.abstractmethod
    def close(self):
        return