import pytest

from image_processor.body_parts import Node, Extremity
from image_processor.utils import Landmark, ExtremityType, Side


@pytest.fixture()
def setup_extremity():
    extremity = Extremity(ExtremityType.HAND, Side.LEFT)
    yield extremity


def test_node_update():
    node1 = Node()
    landmark1: Landmark = {"x": 0, "y": 0, "z": 0, "vis": 1}
    node1.update(landmark1)
    assert node1.x == 0
    assert node1.y == 0
    assert node1.vis == 1


def test_extremity_update(setup_extremity):
    extremity = setup_extremity
    landmark1: Landmark = {"x": 0, "y": 0, "z": 0, "vis": 1}
    landmark2: Landmark = {"x": 0, "y": 0, "z": 0, "vis": 1}
    extremity.update(landmark1, landmark2)
    assert extremity.head.x == 0
    assert extremity.head.y == 0
