import unittest
from modules.overlay import border
from assets.readme_images import Grid_Diagram

class test_motion(unittest.TestCase):

    # Define placeholder node / extremity w. 
    # Define placeholder's .x, .y, .vis
    # Input into function
    # Assert output is correct
    
    # @classmethod
    def setUp(self):
        pass

    def borderDrawing(self):
        newborder = border((0,0,0))
        newborder.draw()

    # @classmethod
    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

