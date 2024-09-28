import unittest
from modules.overlay import border

from modules.body import body
from modules.drumset import drumGrid

class test_motion(unittest.TestCase):
    
    # @classmethod
    def setUp(self):
        pass

    def test_grid(self):
        dg = drumGrid(body())

    # @classmethod
    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()

