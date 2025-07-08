from mediapipe.python.solutions import drawing_utils, pose
from mediapipe.python.solutions.pose import PoseLandmark, Pose
from numpy.typing import NDArray
import logging

# from .utils import Landmark

pose_reader = Pose()


class LandmarkGenerator:
    """Stores dictionary of body landmark locations for current frame."""

    def __init__(self):

        self.length = 33
        self.landmarks_normalized = True
        self.landmarks = None

        pointStructure = dict.fromkeys(["x", "y", "z", "vis"], None)
        self.data = dict.fromkeys(range(self.length), pointStructure)

    def update_data(self, image: NDArray, draw_landmarks: bool) -> None:
        """Updates current landmarks dictionary with input image."""

        allLandmarks = pose_reader.process(image)
        if self.landmarks_normalized:
            self.landmarks = allLandmarks.pose_landmarks
        else:
            self.landmarks = allLandmarks.pose_world_landmarks

        if self.landmarks is None:
            logging.error("No landmarks found")
            return

        for mark in range(self.length):

            coordinate = self.landmarks.landmark[mark]
            self.data[mark] = {
                "x": coordinate.x,
                "y": coordinate.y,
                "vis": coordinate.visibility,
                # 'z': coordinate.z,
            }

        if self.landmarks_normalized:
            for landmark in self.data:
                self.data[landmark]["x"] *= image.shape[1]
                self.data[landmark]["y"] *= image.shape[0]

        if draw_landmarks:
            self.draw_landmarks(image)

    def get_torso_data(self) -> tuple[dict, dict, dict, dict]:

        left_shoulder = self.data[PoseLandmark.LEFT_SHOULDER]
        right_shoulder = self.data[PoseLandmark.RIGHT_SHOULDER]
        left_hip = self.data[PoseLandmark.LEFT_HIP]
        right_hip = self.data[PoseLandmark.RIGHT_HIP]

        return left_shoulder, right_shoulder, left_hip, right_hip

    def get_left_shoulder_data(self) -> dict:

        return self.data[PoseLandmark.LEFT_SHOULDER]

    def get_right_shoulder_data(self) -> dict:

        return self.data[PoseLandmark.RIGHT_SHOULDER]

    def get_left_hip_data(self) -> dict:

        return self.data[PoseLandmark.LEFT_HIP]

    def get_right_hip_data(self) -> dict:

        return self.data[PoseLandmark.RIGHT_HIP]

    def get_left_hand_data(self) -> tuple[dict, dict]:

        left_wrist = self.data[PoseLandmark.LEFT_WRIST]
        left_pinky = self.data[PoseLandmark.LEFT_PINKY]

        return left_wrist, left_pinky

    def get_right_hand_data(self) -> tuple[dict, dict]:

        right_wrist = self.data[PoseLandmark.RIGHT_WRIST]
        right_pinky = self.data[PoseLandmark.RIGHT_PINKY]

        return right_wrist, right_pinky

    def get_left_foot_data(self) -> tuple[dict, dict]:

        left_heel = self.data[PoseLandmark.LEFT_HEEL]
        left_foot_index = self.data[PoseLandmark.LEFT_FOOT_INDEX]

        return left_heel, left_foot_index

    def get_right_foot_data(self) -> tuple[dict, dict]:

        right_heel = self.data[PoseLandmark.RIGHT_HEEL]
        right_foot_index = self.data[PoseLandmark.RIGHT_FOOT_INDEX]

        return right_heel, right_foot_index

    def draw_landmarks(self, image: NDArray) -> None:
        """Uses mediapipe library to draw landmarks inplace on image."""

        drawing_utils.draw_landmarks(
            image,
            self.landmarks,
            connections=pose.POSE_CONNECTIONS,
            landmark_drawing_spec=drawing_utils.DrawingSpec(
                color=(255, 255, 255), thickness=2, circle_radius=2
            ),
            connection_drawing_spec=drawing_utils.DrawingSpec(
                color=(0, 255, 0), thickness=2, circle_radius=1
            ),
        )
