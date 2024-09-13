import unittest
from .motion_project import node, extremity, button, hitCheck, map, updateGrid, avg

class test_motion(unittest.TestCase):

    # Define placeholder node / extremity w. 
    # Define placeholder's .x, .y, .vis
    # Input into function
    # Assert output is correct

    def test_node(self):
        new_node = node(15)
        self.assertEquals(new_node.loc, 15)

if __name__ == '__main__':
    unittest.main()

