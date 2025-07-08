from math import degrees, atan2
from .utils import Side, ExtremityType


class Node:
    """Saves landmark data for a given body node."""

    def __init__(self):

        self.x: float
        self.y: float
        self.vis: float

    def update(self, landmarkData: dict):
        """Stores absolute window coordinate value (x,y) in pixels."""

        self.x = landmarkData["x"]
        self.y = landmarkData["y"]
        self.vis = landmarkData["vis"]


class Torso:
    """Saves information and data of torso, represented with four nodes (left shoulder, right shoulder, left hip, right hip)."""

    def __init__(self):

        self.leftShoulder = Node()
        self.rightShoulder = Node()
        self.leftHip = Node()
        self.rightHip = Node()


class Extremity:
    """Saves information and data of given extremity, represented as a two-point vector with two nodes (head and tail)."""

    queueSize = 3

    # Minimum visibility value for hitCheck
    visMin = 0.5

    # Angular / vertical velocity activation thresholds
    wLim = 20
    vLim = -10

    # Value drop ratio triggers
    wRatio = 0.4
    vRatio = 0.3

    # Hand angle hit threshold
    minAngle = 20
    maxAngle = 150

    # Midrange hit threshold
    midMin = 80
    midMax = 100

    # Min angle change to detect sign change (e.g. + to -)
    angleSwap = 300

    def __init__(self, type: ExtremityType, side: Side):
        """
        - Tail = MediaPipe tail node index (e.g. wrist)
        - Head = MediaPipe head node index (e.g. finger)
        - Type = 'Hand' or 'Foot'
        - Side = 'Right' or 'Left'
        """

        self.tail = Node()
        self.head = Node()
        self.type = type
        self.side = side

        # Angles & angular velocities
        self.angle = []
        self.angVel = []

        # Vertical component and change thereof
        self.vert = []
        self.dVert = []

    def update(self, landmark_data_1: dict, landmark_data_2: dict):

        self.tail.update(landmark_data_1)
        self.head.update(landmark_data_2)
        self._update_angles()

    def check_hit(self) -> bool:
        """Checks extremity for hit based on change in changes in angle or vertical components.
        Seeks for sharp spike in change (velocity) values."""

        # Bypass out-of-frame extremity
        if self.tail.vis < self.visMin and self.head.vis < self.visMin:
            return False

        # Pull extremity angle behavior for hit check calculations
        try:
            a = self.angle[-1]
            w1 = self.angVel[-2]
            w2 = self.angVel[-1]
            v1 = self.dVert[-2]
            v2 = self.dVert[-1]
        except IndexError:
            return False

        # Bypass for angle sign change
        if abs(w2) > self.angleSwap:
            self.angVel.pop(-1)
            return False

        vert_check = False
        # Criteria for enabling Vertical Velocity check
        if self.type == ExtremityType.HAND:
            vert_check = (
                abs(a) < self.minAngle
                or abs(a) > self.maxAngle
                or self.midMin < abs(a) < self.midMax
            )
        elif self.type == ExtremityType.FOOT:
            vert_check = True

        # Check for sharp min in absolute angular velocity / vertical velocity
        leftHit = (
            self.minAngle < a < self.maxAngle
            and w1 < -self.wLim
            and w2 > (self.wRatio * w1)
        )
        rightHit = (
            self.minAngle < (-a) < self.maxAngle
            and w1 > self.wLim
            and w2 < (self.wRatio * w1)
        )
        vert_hit = vert_check and v1 < self.vLim and v2 > (self.vRatio * v1)

        return leftHit or rightHit or vert_hit

    def _update_angles(self):
        """Update angle/vertical components and change rates."""

        # Relative locations normalized to window size
        xDisp = self.head.x - self.tail.x
        yDisp = self.head.y - self.tail.y

        # X and y swapped in tangent function so angle origin is downwards
        theta = degrees(atan2(xDisp, yDisp))
        self.angle.append(theta)

        self.vert.append(-1 * yDisp)

        try:
            dTheta = self.angle[-1] - self.angle[-2]
            self.angVel.append(dTheta)
        except IndexError:
            pass

        try:
            deltaY = self.vert[-1] - self.vert[-2]
            self.dVert.append(deltaY)
        except IndexError:
            pass

        self._pop_stacks()

    def _pop_stacks(self):
        """Clears past data for angles and verticals."""

        if len(self.angVel) > self.queueSize:
            self.angle.pop(0)
            self.angVel.pop(0)

        if len(self.dVert) > self.queueSize:
            self.vert.pop(0)
            self.dVert.pop(0)
