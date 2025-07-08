"""Contains tools for defining the user's body features and locations
frame-by-frame via a landmark-processing library."""

from .landmark_generator import LandmarkGenerator
from .drum_grid import DrumGrid
from .utils import State, Side, ExtremityType
from .body_parts import Node, Extremity


class Body:
    """Holds all landmark data and aggregates into extremity and torso data."""

    vis_threshold = 0.5
    open_hat_angle = 70

    def __init__(self, camera_width: int, camera_height: int):

        # Torso definitions
        leftShoulder = Node()
        rightShoulder = Node()
        leftHip = Node()
        rightHip = Node()

        # Limb definitions
        leftHand = Extremity(
            ExtremityType.HAND,
            Side.LEFT,
        )
        rightHand = Extremity(
            ExtremityType.HAND,
            Side.RIGHT,
        )
        leftFoot = Extremity(
            ExtremityType.FOOT,
            Side.LEFT,
        )
        rightFoot = Extremity(
            ExtremityType.FOOT,
            Side.RIGHT,
        )

        self.torso = [leftShoulder, rightShoulder, leftHip, rightHip]
        self.extremities = [leftHand, rightHand, leftFoot, rightFoot]
        self.landmark_processor = LandmarkGenerator()

        self.cam_width = camera_width
        self.cam_height = camera_height

        self.drum_grid = DrumGrid(camera_width, camera_height)

    def process_frame(self, frame, draw_landmarks: bool = True) -> State:
        """Updates body attributes for given frame,
        including locations and inFrame status."""

        self.landmark_processor.update_data(frame, draw_landmarks)
        self._update_components()

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
            if point.vis < self.vis_threshold or not (
                0 < point.x < self.cam_width and 0 < point.y < self.cam_height
            ):
                return False

        return True

    def _check_hihat_open(self):
        """Set hihat to open or closed."""

        if (
            abs(self.extremities[2].angle[-1]) > self.open_hat_angle
            and self.extremities[2].head.vis > self.vis_threshold
        ):
            self.drum_grid.set_hihat_open(True)
        else:
            self.drum_grid.set_hihat_open(False)

    def _update_components(self):

        left_shoulder_data, right_shoulder_data, left_hip_data, right_hip_data = (
            self.landmark_processor.get_torso_data()
        )

        self.torso[0].update(left_shoulder_data)
        self.torso[1].update(right_shoulder_data)
        self.torso[2].update(left_hip_data)
        self.torso[3].update(right_hip_data)

        left_wrist_data, left_pinky_data = self.landmark_processor.get_left_hand_data()
        self.extremities[0].update(left_wrist_data, left_pinky_data)

        right_wrist_data, right_pinky_data = (
            self.landmark_processor.get_right_hand_data()
        )
        self.extremities[1].update(right_wrist_data, right_pinky_data)

        left_heel_data, left_foot_index_data = (
            self.landmark_processor.get_left_foot_data()
        )
        self.extremities[2].update(left_heel_data, left_foot_index_data)

        right_heel_data, right_foot_index_data = (
            self.landmark_processor.get_right_foot_data()
        )
        self.extremities[3].update(right_heel_data, right_foot_index_data)
