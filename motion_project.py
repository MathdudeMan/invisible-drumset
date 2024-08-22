import cv2
import mediapipe as mp
from math import degrees, atan2
import numpy as np
import pygame


class extremity:
    def __init__(self, tail = int, head = int):
        
        # Tail and head of foot / hand vector, pointed outward
        self.tail = tail
        self.tailX = int
        self.tailY = int

        self.head = head
        self.headX = int
        self.headY = int

        self.angle = [] #Vector angle values
        self.angVel = [] #Angular velocity values

    def addAngle(self):
        
        deltaX = capWidth * (self.headX - self.tailX)
        deltaY = capHeight * (self.headY - self.tailY)

        #Angle value normalized to degree range -180 : 180, w. origin shifted to floor
        theta = degrees(atan2(deltaY, deltaX)) + 90
        self.angle.append(theta)

        if len(self.angle) > 1:
            change = self.angle[-1] - self.angle[-2]
            self.angVel.append(change)


def PoseDetection():

    while True:

        # Read & process image
        success, img = cap.read()
        if not success:
            break

        img = cv2.resize(img, (800, 600))
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = vid_pose.process(imgRGB)

        # Read & draw all landmarks
        landmarks = results.pose_landmarks

        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), connection_drawing_spec = mp_drawing.DrawingSpec(color = (255,0,255), thickness = 2, circle_radius = 1))

        # Show frame
        cv2.imshow("Image", img)


        # Get hand / foot landmarks
        for mark in range(33):
            data_point = landmarks.landmark[mark]
            dic[mark] = {
                'x': data_point.x,
                'y': data_point.y,
                'z': data_point.z,
                'vis': data_point.visibility}

        for item in limbs:
            hitCheck(item)

        # Press Q on keyboard to exit, else wait 1ms
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def hitCheck(limb):

    #Update extremity vector locations, visibility
    limb.tailX = dic[limb.tail]['x']
    limb.tailY = dic[limb.tail]['y']
    limb.tailVis = dic[limb.tail]['vis']

    limb.headX = dic[limb.head]['x']
    limb.headY = dic[limb.head]['y']
    limb.headVis = dic[limb.head]['vis']

    # If extremity visible, update angles
    if limb.tailVis > 0.3 and limb.headVis > 0.3:
        limb.addAngle()
    else:
        return

    if len(limb.angVel) < 2:
        return

    a = limb.angle[-1]
    v = limb.angVel[-2]
    w = limb.angVel[-1]

    R = 15 #Downward angular velocity activation threshhold

    rightHit = a > 0 and v < -R and 0.2*v < w
    leftHit = a < 0 and v > R and 0.2*v > w

    if leftHit or rightHit:
        
        pygame.mixer.music.load('Motion-Project/Audio/596890__stoltingmediagroup__smg_sound_drum_hat_0000035927.wav')
        pygame.mixer.music.play()

        mapNum = map(limb)
        #playSound(mapNum)

    return


def map(limb):
    # Determine region of appendage, indexed 1 - 16
    
    mapNum = 0

    x = limb.headX
    y = limb.headY
    
    # x Check
    if x < gridRanges[1]:
        mapNum += 1
    elif x < gridRanges[2]:
        mapNum += 2
    elif x < gridRanges[3]:
        mapNum += 3
    else:
        mapNum += 4

    # y Check
    if y < gridRanges[1]:
        pass
    elif y < gridRanges[2]:
        mapNum += 4
    elif y < gridRanges[3]:
        mapNum += 8
    else:
        mapNum += 12

    return mapNum


def playSound(mapNum = int):

    sounds = {
        1: "Cymbal 1", # Get soundfile, implement here
        2: "Cymbal 2",
        3: "Cymbal 3",
        4: "Cymbal 4",
        5: "Ride",
        6: "Tom 2",
        7: "Tom 1",
        8: "Hi Hat",
        9: "Floor Tom",
        10: "Snare",
        11: "Snare",
        12: "Cowbell",
        13: "Cat",
        14: "BD",
        15: "Floor Hi Hat",
        16: "Whoopie Cushion"
    }

    pygame.mixer.music.load('Motion-Project/Audio/596890__stoltingmediagroup__smg_sound_drum_hat_0000035927.wav')

    #pygame.mixer.music.load(sounds[mapNum])
    pygame.mixer.music.play()

####################################################

pygame.mixer.init()

# Init mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Init video pose object
vid_pose = mp_pose.Pose()

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = cap.get(3)
capHeight = cap.get(4)

# Limb definitions
leftHand = extremity(15,19)
rightHand = extremity(16,20)
leftFoot = extremity(29,31)
rightFoot = extremity(30,32)

limbs = [leftHand, rightHand, leftFoot, rightFoot]

# Sound grid ranges
gridRanges = [[0,0.3,0.5,0.7,1], [0,0.25,0.5,0.75,1]]

#init landmark dictionary
coordinate = dict.fromkeys(['x','y','z','vis'], None)
dic = dict.fromkeys(range(33), coordinate)


PoseDetection()


cap.release()
cv2.destroyAllWindows()
