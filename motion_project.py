import cv2
import mediapipe as mp
from math import degrees, atan2
import matplotlib.pyplot as plt
import pygame
from playsound import playsound


class extremity:
    def __init__(self, tail = int, head = int):
        
        # Tail and head of foot / hand vector, pointed outward
        self.tail = tail
        self.tailX = int
        self.tailY = int
        self.tailVis = int

        self.head = head
        self.headX = int
        self.headY = int
        self.tailVis = int

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

        try:
            for mark in range(33):
                data_point = landmarks.landmark[mark]
                dic[mark] = {
                    'x': data_point.x,
                    'y': data_point.y,
                    'z': data_point.z,
                    'vis': data_point.visibility}
        except AttributeError:
            pass

        for item in limbs:
            hitCheck(item)

        # Press Q on keyboard to exit, else wait 1ms
        if cv2.waitKey(3) & 0xFF == ord('q'):
            break


def hitCheck(limb):

    #Update extremity vector locations, visibility
    limb.tailX = dic[limb.tail]['x']
    limb.tailY = dic[limb.tail]['y']
    limb.tailVis = dic[limb.tail]['vis']

    limb.headX = dic[limb.head]['x']
    limb.headY = dic[limb.head]['y']
    limb.headVis = dic[limb.head]['vis']

    # Minimum visibility value for hit
    visMin = 0.5

    # If extremity visible, update angles
    if limb.tailVis > visMin and limb.headVis > visMin:
        limb.addAngle()
    else:
        return

    if len(limb.angVel) < 2:
        return

    a = limb.angle[-1]
    v = limb.angVel[-2]
    w = limb.angVel[-1]

    R = 10 #Downward angular velocity activation threshold

    rightHit = a > 0 and v > R and 0.5*v > w
    leftHit = a < 0 and v < -R and 0.5*v < w

    if leftHit or rightHit:
        
        mapNum = map(limb)

        print("hit", len(limb.angle), mapNum, limb.headVis)

        playSound(mapNum)

    return


def map(limb):
    # Determine region of appendage, indexed 1 - 16
    
    mapNum = 0

    x = limb.headX
    y = limb.headY
    
    # x Check
    if x < gridRanges[0][1]:
        mapNum += 1
    elif x < gridRanges[0][2]:
        mapNum += 2
    elif x < gridRanges[0][3]:
        mapNum += 3
    else:
        mapNum += 4

    # y Check
    if y < gridRanges[1][1]:
        pass
    elif y < gridRanges[1][2]:
        mapNum += 4
    elif y < gridRanges[1][3]:
        mapNum += 8
    else:
        mapNum += 12

    return mapNum


def playSound(mapNum = int):

    sounds = {
        1: "./Motion-Project/Drum Sounds/Samples/tom-fm.wav", # Get soundfile, implement here
        2: "./Motion-Project/Drum Sounds/Samples/crash-acoustic.wav",
        3: "./Motion-Project/Drum Sounds/Samples/crash-noise.wav",
        4: "./Motion-Project/Drum Sounds/Samples/openhat-analog.wav",
        5: "./Motion-Project/Drum Sounds/Samples/ride-acoustic01.wav",
        6: "./Motion-Project/Drum Sounds/Samples/tom-acoustic02.wav",
        7: "./Motion-Project/Drum Sounds/Samples/tom-acoustic01.wav",
        8: "./Motion-Project/Drum Sounds/Samples/hihat-plain.wav",
        9: "./Motion-Project/Drum Sounds/Samples/tom-rototom.wav",
        10: "./Motion-Project/Drum Sounds/Samples/snare-acoustic01.wav",
        11: "./Motion-Project/Drum Sounds/Samples/snare-acoustic01.wav",
        12: "./Motion-Project/Drum Sounds/Samples/perc-metal.wav",
        13: "./Motion-Project/Drum Sounds/Samples/openhat-analog.wav",
        14: "./Motion-Project/Drum Sounds/Samples/kick-classic.wav",
        15: "./Motion-Project/Drum Sounds/Samples/hihat-plain.wav",
        16: "./Motion-Project/Drum Sounds/Samples/kick-gritty.wav"
    }

    playsound(sounds[mapNum], block = False)


####################################################

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

for limb in limbs:
    plt.subplot(1,2,1)
    plt.plot([x for x in range(len(limb.angle))], limb.angle, label = "angle")
    plt.subplot(1,2,2)
    plt.plot([x for x in range(len(limb.angVel))], limb.angVel, label = "theta")

plt.show()
plt.legend()

cap.release()
cv2.destroyAllWindows()
