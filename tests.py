import unittest
from .motion_project import node

class test_motion(unittest.TestCase):

    def test_node(self):
        new_node = node(15)
        self.assertEquals(new_node.loc, 15)

if __name__ == '__main__':
    unittest.main()

