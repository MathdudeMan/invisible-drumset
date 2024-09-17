import unittest
from .motion_project import node, extremity, button, hitCheck, map, avg

class test_motion(unittest.TestCase):

    # Define placeholder node / extremity w. 
    # Define placeholder's .x, .y, .vis
    # Input into function
    # Assert output is correct
    
    # @classmethod
    def setUp(self):
        sampleExt = extremity(1, 2, 'Hand', 'Left')


        sampleBtn = button(0.05, 0.25, 0.05, 0.15)


        sampleGrid = None

        sampleTorso = [node(1), node(2), node(3), node(4)]

    # @classmethod
    def tearDown(self):
        pass

    def test_node(self):
        new_node = node(15)
        self.assertEquals(new_node.loc, 15)

    def test_falseHit(self):
        pass

    def test_firstFrame(self):
        pass

    def test_handHit(self):
        pass

    def test_footHit(self):
        pass

    def test_mapOutside(self):
        pass

    def test_mapFoot(self):
        pass

    def test_mapButton(self):
        pass

    def test_mapSound(self):
        #Pick random location, create mapping
        pass



if __name__ == '__main__':
    unittest.main()

