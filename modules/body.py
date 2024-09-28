"""Contains tools for defining the user's body features and locations via Mediapipe pose estimation library."""

import mediapipe as mp
from math import degrees, atan2

# Init mediapipe pose class, video pose object
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
vid_pose = mp_pose.Pose()

class body:
    """Holds all landmark data and aggregates into extremity and torso data."""

    def __init__(self, window):

        # Torso definitions
        leftShoulder = node(11)
        rightShoulder = node(12)
        leftHip = node(23)
        rightHip = node(24)

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
        self.inFrame = False

    def update(self, frame):
        """Updates body attributes for given frame, including locations and inFrame status."""

        self.landmarks.updateData(frame)
        self._updateComponents(self.landmarks.data)
        self.inFrame = self._frameCheck()
    
    def _updateComponents(self, landmarkData):
        
        for node in self.torso:
            node.update(landmarkData, self.maxX, self.maxY)

        for extremity in self.extremities:
            extremity.update(landmarkData, self.maxX, self.maxY)

    def _frameCheck(self):
        """Returns boolean denoting if all 4 torso nodes are in frame."""
        
        for point in self.torso:
            if point.vis < 0.5:
                return False
            
        return True
    

class landmarks:
    """Stores dictionary of body landmark locations for current frame."""

    def __init__(self, length):
        
        pointStructure = dict.fromkeys(['x','y','z','vis'], None)
        self.length = length
        self.rawData = None
        self.data = dict.fromkeys(range(self.length), pointStructure)

    def updateData(self, image):
        """Updates current landmarks dictionary given current image."""

        allLandmarks = vid_pose.process(image)
        self.rawData = allLandmarks.pose_landmarks
        if self.rawData is not None:
            self._extract(self.rawData)

    def _extract(self, rawData):

        for mark in range(self.length):

            coordinate = rawData.landmark[mark]
            self.data[mark] = {
                'x': coordinate.x,
                'y': coordinate.y,
                'vis': coordinate.visibility
                # 'z': markCoord.z,
                }
            
    def draw(self, frame):
        """Uses mediapipe library to draw landmarks on current frame. 
        Uses input of only a given frame image, not requiring frame size parameters.
        
        *(Called by draw client in overlay.py.)*"""

        mp_drawing.draw_landmarks(frame, self.rawData, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 1))


class node:
    """Saves landmark data for an given mediapipe node."""

    def __init__(self, id = int):

        self.id = id
        self.x = float
        self.y = float
        self.vis = float

    def update(self, landmarkData, windowWidth, windowHeight):
        """Stores absolute window coordinate value (x,y) in pixels."""

        self.x = landmarkData[self.id]['x'] * windowWidth
        self.y = landmarkData[self.id]['y'] * windowHeight
        self.vis = landmarkData[self.id]['vis']


class extremity:
    """Saves information and data on given extremity, represented as a two-point vector with two nodes (head and tail)."""
        
    def __init__(self, tail = int, head = int, type = '', side = ''):
        """
        - Tail = MediaPipe tail node index (e.g. wrist)
        - Head = MediaPipe head node index (e.g. finger)
        - Type = 'Hand' or 'Foot'
        - Side = 'Right' or 'Left'
        """

        self.tail = node(tail)
        self.head = node(head)
        self.type = type
        self.side = side

        # Angles & angular velocities
        self.angle = [] 
        self.angVel = []

        # Vertical component and change thereof
        self.vert = []
        self.dVert = []

    def update(self, landmarkData, windowWidth, windowHeight):

        self.tail.update(landmarkData, windowWidth, windowHeight)
        self.head.update(landmarkData, windowWidth, windowHeight)
        self.updateAngles()

    def updateAngles(self):
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

        self._cleanup()

    def _cleanup(self):
        """ Clears past data for angles and verticals."""

        if len(self.angVel) > 3:
            self.angle.pop(0)
            self.angVel.pop(0)

        if len(self.dVert) > 3:
            self.vert.pop(0)
            self.dVert.pop(0)
