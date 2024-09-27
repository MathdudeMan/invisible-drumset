"""
Contains tools for defining the user's body features and locations via pose estimation.
"""

import mediapipe as mp
from math import degrees, atan2

# Init mediapipe pose class, video pose object
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
vid_pose = mp_pose.Pose()

class body:
    """Holds all landmark data and aggregates into extremity and torso data."""

    def __init__(self):

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
        self.inFrame = False

    def update(self, frame):
        """Updates body attributes, including locations and inFrame determination."""

        self.landmarks.updateData(frame)
        self._updateTorso(self.landmarks.data)
        self._updateExtremities(self.landmarks.data)
        self.inFrame = self._frameCheck()
    
    def _updateTorso(self, landmarkData):
        
        for node in self.torso:
            node.updateNode(landmarkData)

    def _updateExtremities(self, landmarkData):

        for object in self.extremities:
            object.tail.updateNode(landmarkData)
            object.head.updateNode(landmarkData)

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
        """Update current data dictionary with user landmark locations."""

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
        
        _(Called in overlay.py.)_"""

        mp_drawing.draw_landmarks(frame, self.rawData, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 1))


class node:
    """Saves landmark data of an important node."""

    def __init__(self, loc = int):
        self.loc = loc
        self.x = float
        self.y = float
        self.vis = float

    def updateNode(self, landmarkData = {}):
        self.x = landmarkData[self.loc]['x']
        self.y = landmarkData[self.loc]['y']
        self.vis = landmarkData[self.loc]['vis']


class extremity:
    def __init__(self, tail = int, head = int, type = '', side = ''):
        """Saves information and data on given extremity, represented by two nodes (head and tail)"""

        self.type = type # Possible values 'Hand' and 'Foot'
        self.side = side # 'Right' or 'Left'

        # Tail and head of foot / hand vector, pointed outward from base of extremity
        self.tail = node(tail)
        self.head = node(head)

        self.angle = [] # Vector angle values
        self.angVel = [] # Angular velocity values
        self.vert = [] # Delta Y values
        self.dVert = [] # Change in delta Y (rel. velocity of head)

    def addAngle(self, window):
        
        # FIXME window
        # Distances relative to screen (i.e. 0.0 - 1.0) converted to absolute distances
        xDisp = window.capWidth * (self.head.x - self.tail.x)
        yDisp = window.capHeight * (self.head.y - self.tail.y)

        # Angle value normalized to degree range -180 : 180, w. origin shifted to floor
        theta = degrees(atan2(xDisp, yDisp))
        self.angle.append(theta)

        if len(self.angle) > 1:
            dTheta = self.angle[-1] - self.angle[-2]
            self.angVel.append(dTheta)

        # Update change in delta-Y for vertical hit check
        self.vert.append(-1 * yDisp)
        if len(self.vert) > 1:
            deltaY = self.vert[-1] - self.vert[-2]
            self.dVert.append(deltaY)

        self.__cleanup()
        
    def __cleanup(self):
        # Angle / delta-Y queue cleanup - comment out during data display 
        if len(self.angVel) > 3:
            self.angle.pop(0)
            self.angVel.pop(0)

        if len(self.dVert) > 3:
            self.vert.pop(0)
            self.dVert.pop(0)
