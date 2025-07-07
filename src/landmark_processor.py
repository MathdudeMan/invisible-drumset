from mediapipe.python.solutions import pose, drawing_utils
from numpy.typing import NDArray

import logging

pose_reader = pose.Pose()

nose = pose.PoseLandmark.NOSE


class LandmarkProcessor:
    """Stores dictionary of body landmark locations for current frame."""

    def __init__(self):

        self.length = 33
        self.landmarks_normalized = None

        pointStructure = dict.fromkeys(["x", "y", "z", "vis"], None)
        self.data = dict.fromkeys(range(self.length), pointStructure)

    def update_data(self, image: NDArray, draw_landmarks: bool) -> None:
        """Updates current landmarks dictionary with input image."""

        allLandmarks = pose_reader.process(image)
        self.landmarks_normalized = allLandmarks.pose_landmarks
        # landmarks_world = allLandmarks.pose_world_landmarks

        if self.landmarks_normalized is None:
            logging.error("No landmarks found")
            return

        for mark in range(self.length):

            coordinate = self.landmarks_normalized.landmark[mark]
            self.data[mark] = {
                "x": coordinate.x,
                "y": coordinate.y,
                "vis": coordinate.visibility,
                # 'z': coordinate.z,
            }

        if draw_landmarks:
            self._draw(image)

    def get_hand_data(self):
        return self.landmarks_normalized.landmark[pose.PoseLandmark.LEFT_INDEX]

    def _draw(self, image: NDArray) -> None:
        """Uses mediapipe library to draw landmarks inplace on image."""

        drawing_utils.draw_landmarks(
            image,
            self.landmarks_normalized,
            connections=pose.POSE_CONNECTIONS,
            landmark_drawing_spec=drawing_utils.DrawingSpec(
                color=(255, 255, 255), thickness=2, circle_radius=2
            ),
            connection_drawing_spec=drawing_utils.DrawingSpec(
                color=(0, 255, 0), thickness=2, circle_radius=1
            ),
        )
