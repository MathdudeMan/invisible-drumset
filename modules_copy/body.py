"""Contains tools for defining the user's body features and locations
    frame-by-frame via Google's Mediapipe pose estimation library."""

from math import degrees, atan2

from .pose import landmarks

# Init mediapipe pose class, video pose object


class body:
    """Holds all landmark data and aggregates into extremity and torso data."""

    def __init__(self, window):

        # Torso definitions
        leftShoulder = mp_Node(11)
        rightShoulder = mp_Node(12)
        leftHip = mp_Node(23)
        rightHip = mp_Node(24)

        # Limb definitions
        leftHand = extremity(15, 17, 'Hand', 'Left')
        rightHand = extremity(16, 18, 'Hand', 'Right')
        leftFoot = extremity(29, 31, 'Foot', 'Left')
        rightFoot = extremity(30, 32, 'Foot', 'Right')

        self.torso = [leftShoulder, rightShoulder, leftHip, rightHip]
        self.extremities = [leftHand, rightHand, leftFoot, rightFoot]
        self.landmarks = landmarks(33)

        self.maxX = window.width
        self.maxY = window.height
        self.isInFrame = False

    def update(self, frame):
        """Updates body attributes for given frame, including locations and inFrame status."""

        self.landmarks.update_data(frame)
        self._update_components(self.landmarks.data)
        self.isInFrame = self._check_in_frame()
    
    def _update_components(self, landmarkData):
        
        for node in self.torso:
            node.update(landmarkData, self.maxX, self.maxY)

        for extremity in self.extremities:
            extremity.update(landmarkData, self.maxX, self.maxY)

    def _check_in_frame(self) -> bool:
        """Returns boolean denoting if all 4 torso nodes are in frame."""
        
        for point in self.torso:
            if point.vis < 0.5 or not (0 < point.x < self.maxX and 0 < point.y < self.maxY):
                return False
            
        return True
            

class mp_Node:
    """Saves landmark data for a given mediapipe node."""

    def __init__(self, id: int):

        self.id = id
        self.x: float
        self.y: float
        self.vis: float

    def update(self, landmarkData: dict, windowWidth: int, windowHeight: int):
        """Stores absolute window coordinate value (x,y) in pixels."""

        self.x = landmarkData[self.id]['x'] * windowWidth
        self.y = landmarkData[self.id]['y'] * windowHeight
        self.vis = landmarkData[self.id]['vis']


class extremity:
    """Saves information and data of given extremity, represented as a two-point vector with two nodes (head and tail)."""
        
    def __init__(self, tail: int, head: int, type: str, side: str):
        """
        - Tail = MediaPipe tail node index (e.g. wrist)
        - Head = MediaPipe head node index (e.g. finger)
        - Type = 'Hand' or 'Foot'
        - Side = 'Right' or 'Left'
        """

        self.tail = mp_Node(tail)
        self.head = mp_Node(head)
        self.type = type
        self.side = side

        # Angles & angular velocities
        self.angle = [] 
        self.angVel = []

        # Vertical component and change thereof
        self.vert = []
        self.dVert = []

    def update(self, landmarkData: dict, windowWidth: int, windowHeight: int):

        self.tail.update(landmarkData, windowWidth, windowHeight)
        self.head.update(landmarkData, windowWidth, windowHeight)
        self._updateAngles()

    def _updateAngles(self):
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

        if len(self.angVel) > 3:
            self.angle.pop(0)
            self.angVel.pop(0)

        if len(self.dVert) > 3:
            self.vert.pop(0)
            self.dVert.pop(0)

