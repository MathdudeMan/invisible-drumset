import logging
from enum import IntEnum
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarksConnections
from numpy.typing import NDArray

from .utils import Landmark

MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "models"
    / "pose_landmarker_lite.task"
)
logger = logging.getLogger(__name__)


class PoseLandmark(IntEnum):
    """Indices defined by the MediaPipe Pose Landmarker model."""

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


def create_pose_landmarker() -> vision.PoseLandmarker:
    options = vision.PoseLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.IMAGE,
        num_poses=1,
    )
    return vision.PoseLandmarker.create_from_options(options)


class LandmarkGenerator:
    """Stores dictionary of body landmark locations for current frame."""

    def __init__(self, pose_reader: vision.PoseLandmarker | None = None):
        self.length = 33
        self.landmarks_normalized = True
        self.landmarks = None
        self.data: dict[int, Landmark] = {}
        self.pose_reader = pose_reader or create_pose_landmarker()

    def update_data(self, image: NDArray, draw_landmarks: bool) -> None:
        """Updates current landmarks dictionary with input image."""

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        result = self.pose_reader.detect(mp_image)

        landmark_sets = (
            result.pose_landmarks
            if self.landmarks_normalized
            else result.pose_world_landmarks
        )
        if not landmark_sets:
            self.landmarks = None
            self.data.clear()
            logger.error("No landmarks found")
            return

        self.landmarks = landmark_sets[0]
        for mark, coordinate in enumerate(self.landmarks):
            self.data[mark] = {
                "x": coordinate.x,
                "y": coordinate.y,
                "z": coordinate.z,
                "vis": coordinate.visibility,
            }

        if self.landmarks_normalized:
            for landmark in self.data.values():
                landmark["x"] *= image.shape[1]
                landmark["y"] *= image.shape[0]

        if draw_landmarks:
            self.draw_landmarks(image, result.pose_landmarks[0])

    def get_torso_data(self) -> tuple[Landmark, Landmark, Landmark, Landmark]:
        left_shoulder = self.data[PoseLandmark.LEFT_SHOULDER]
        right_shoulder = self.data[PoseLandmark.RIGHT_SHOULDER]
        left_hip = self.data[PoseLandmark.LEFT_HIP]
        right_hip = self.data[PoseLandmark.RIGHT_HIP]

        return left_shoulder, right_shoulder, left_hip, right_hip

    def get_left_shoulder_data(self) -> Landmark:
        return self.data[PoseLandmark.LEFT_SHOULDER]

    def get_right_shoulder_data(self) -> Landmark:
        return self.data[PoseLandmark.RIGHT_SHOULDER]

    def get_left_hip_data(self) -> Landmark:
        return self.data[PoseLandmark.LEFT_HIP]

    def get_right_hip_data(self) -> Landmark:
        return self.data[PoseLandmark.RIGHT_HIP]

    def get_left_hand_data(self) -> tuple[Landmark, Landmark]:
        left_wrist = self.data[PoseLandmark.LEFT_WRIST]
        left_pinky = self.data[PoseLandmark.LEFT_PINKY]

        return left_wrist, left_pinky

    def get_right_hand_data(self) -> tuple[Landmark, Landmark]:
        right_wrist = self.data[PoseLandmark.RIGHT_WRIST]
        right_pinky = self.data[PoseLandmark.RIGHT_PINKY]

        return right_wrist, right_pinky

    def get_left_foot_data(self) -> tuple[Landmark, Landmark]:
        left_heel = self.data[PoseLandmark.LEFT_HEEL]
        left_foot_index = self.data[PoseLandmark.LEFT_FOOT_INDEX]

        return left_heel, left_foot_index

    def get_right_foot_data(self) -> tuple[Landmark, Landmark]:
        right_heel = self.data[PoseLandmark.RIGHT_HEEL]
        right_foot_index = self.data[PoseLandmark.RIGHT_FOOT_INDEX]

        return right_heel, right_foot_index

    def draw_landmarks(self, image: NDArray, landmarks) -> None:
        """Draw Tasks landmarks in place on an OpenCV image."""

        height, width = image.shape[:2]
        points = [
            (int(landmark.x * width), int(landmark.y * height))
            for landmark in landmarks
        ]
        for connection in PoseLandmarksConnections.POSE_LANDMARKS:
            cv2.line(
                image,
                points[connection.start],
                points[connection.end],
                color=(0, 255, 0),
                thickness=2,
            )
        for point in points:
            cv2.circle(image, point, radius=2, color=(255, 255, 255), thickness=2)
