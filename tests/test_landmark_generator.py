from types import SimpleNamespace

import numpy as np

from image_processor.landmark_generator import LandmarkGenerator, PoseLandmark


class FakePoseLandmarker:
    def __init__(self, result):
        self.result = result

    def detect(self, image):
        return self.result


def test_tasks_landmarks_preserve_pixel_coordinate_contract():
    landmarks = [
        SimpleNamespace(x=0.25, y=0.5, z=float(index), visibility=0.9)
        for index in range(33)
    ]
    result = SimpleNamespace(
        pose_landmarks=[landmarks], pose_world_landmarks=[landmarks]
    )
    generator = LandmarkGenerator(FakePoseLandmarker(result))

    generator.update_data(np.zeros((100, 200, 3), dtype=np.uint8), False)

    left_wrist, left_pinky = generator.get_left_hand_data()
    assert left_wrist == {"x": 50.0, "y": 50.0, "z": 15.0, "vis": 0.9}
    assert left_pinky["z"] == PoseLandmark.LEFT_PINKY


def test_no_pose_clears_previous_landmark_data():
    result = SimpleNamespace(pose_landmarks=[], pose_world_landmarks=[])
    generator = LandmarkGenerator(FakePoseLandmarker(result))
    generator.data[0] = {"x": 1, "y": 1, "z": 1, "vis": 1}

    generator.update_data(np.zeros((100, 200, 3), dtype=np.uint8), False)

    assert generator.landmarks is None
    assert generator.data == {}
