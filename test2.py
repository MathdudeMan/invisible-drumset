import cv2
import mediapipe as mp
import math
import sys

class limb:
    def __init__(self, tail = int, head = int):
        self.tail = tail
        self.tailX = int
        self.tailY = int
        self.tailVis = int

        self.head = head
        self.headX = int
        self.headY = int
        self.headVis = int

        self.angle = [] #Vector angle values
        self.delta = [] #Angular velocity values

    def addAngle(self):
        
        deltaX = self.headX - self.tailX
        deltaY = self.headY - self.tailY
        theta = math.atan2(deltaX, deltaY)

        self.angle.append(theta)

        if len(self.delta) > 1:
            change = self.angle[-1] - self.angle[-2]
            self.delta.append(change)


# Init mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Init video pose object
vid_pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Activate Video / Webcam
cap = cv2.VideoCapture(0)

# Read & process image
success, img = cap.read()
if not success:
    pass

img = cv2.resize(img, (800, 600))
imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
results = vid_pose.process(imgRGB)

# Read all landmarks
landmarks = results.pose_landmarks


# Limb definitions
leftHand = limb(15,19)
rightHand = limb(16,20)
leftFoot = limb(29,31)
rightFoot = limb(30,32)

limbs = [leftHand, rightHand, leftFoot, rightFoot]
    
# Hand / foot landmark updates
dic = {}
for mark, data_point in zip(range(0,32), landmarks.landmark):
    dic[mark] = dict(
        x = data_point.x,
        y = data_point.y,
        z = data_point.z,
        vis = data_point.visibility)
    
for item in limbs:
    item.tailX = dic[item.tail]['x']
    item.tailY = dic[item.tail]['y']
    item.headX = dic[item.head]['x']
    item.headY = dic[item.head]['y']

    item.addAngle()