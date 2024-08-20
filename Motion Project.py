import cv2
import numpy as np
import mediapipe as mp
import numpy as np
import pygame
from Test import *

# Init mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Init video pose object
vid_pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Activate Video / Webcam
cap = cv2.VideoCapture(0)

# Setup pose landmarks
markPairs = [(15,19),(16,20),(29,31),(30,32)]
limbs = ["leftHand", "rightHand", "leftFoot", "rightFoot"]

limbs = []

leftHand = limb(15,19)
rightHand = limb(16,20)
leftFoot = limb(29,31)
rightFoot = limb(30,32)

limbs.append(leftHand)



gridRanges = [[0,0.3,0.5,0.7,1], [0,0.25,0.5,0.75,1]]

markNames = ()
for num in goodMarks:
    markNames += (mp_pose.PoseLandmark(num), )


# Get hand / foot landmarks
dic = {}
for mark, data_point in zip(markNames, landmarks.PoseLandmark):
    dic[mark.value] = dict(index = mark.name, 
        x = data_point.x,
        y = data_point.y,
        z = data_point.z,
        vis = data_point.visibility)




    
success, img = cap.read()
if success == True:

    PoseDetection() # This is main while loop


cap.release()
cv2.destroyAllWindows()