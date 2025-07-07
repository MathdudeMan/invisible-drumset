"""Contains tools for defining the user's body features and locations
frame-by-frame via Google's Mediapipe pose estimation library."""

from .landmark_processor import LandmarkProcessor

from .drum_grid import DrumGrid
from .enums import State
from .body_parts import Node, Extremity


class Body:
    """Holds all landmark data and aggregates into extremity and torso data."""

    def __init__(self, camera_width: int, camera_height: int):

        # Torso definitions
        leftShoulder = Node(11)
        rightShoulder = Node(12)
        leftHip = Node(23)
        rightHip = Node(24)

        # Limb definitions
        leftHand = Extremity(15, 17, "Hand", "Left")
        rightHand = Extremity(16, 18, "Hand", "Right")
        leftFoot = Extremity(29, 31, "Foot", "Left")
        rightFoot = Extremity(30, 32, "Foot", "Right")

        self.torso = [leftShoulder, rightShoulder, leftHip, rightHip]
        self.extremities = [leftHand, rightHand, leftFoot, rightFoot]
        self.landmark_processor = LandmarkProcessor()

        self.cam_width = camera_width
        self.cam_height = camera_height

        self.drum_grid = DrumGrid(camera_width, camera_height)

    def process_frame(self, frame, draw_landmarks: bool = True) -> State:
        """Updates body attributes for given frame, including locations and inFrame status."""

        self.landmark_processor.update_data(frame, draw_landmarks)
        self._update_components(self.landmark_processor.data)

        self.drum_grid.update_gridlines(
            self.torso[0], self.torso[1], self.torso[2], self.torso[3]
        )

        if self._check_in_frame():

            self._check_hihat_open()

            for extremity in self.extremities:
                mapping = self.drum_grid.get_location_id(extremity, True)
                self.drum_grid.play_drum(extremity, mapping)

            if self.drum_grid.sound_active:
                return State.ON
            else:
                return State.OFF
        else:
            self.drum_grid.sound_active = False
            return State.OUT

    def _check_in_frame(self) -> bool:
        """Returns boolean denoting if all 4 torso nodes are in frame."""

        for point in self.torso:
            if point.vis < 0.5 or not (
                0 < point.x < self.cam_width and 0 < point.y < self.cam_height
            ):
                return False

        return True

    def _check_hihat_open(self):
        """Set hihat to open or closed."""

        open_hat_angle = 70
        vis_threshold = 0.5
        if (
            abs(self.extremities[2].angle[-1]) > open_hat_angle
            and self.extremities[2].head.vis > vis_threshold
        ):
            self.drum_grid.set_hihat_open(True)
        else:
            self.drum_grid.set_hihat_open(False)

    def _update_components(self, landmarkData):

        for node in self.torso:
            node.update(landmarkData, self.cam_width, self.cam_height)

        for extremity in self.extremities:
            extremity.update(landmarkData, self.cam_width, self.cam_height)
