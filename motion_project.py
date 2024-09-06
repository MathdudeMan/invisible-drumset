import cv2
import mediapipe as mp
from math import degrees, atan2
from playsound import playsound
import tkinter as tk
import numpy as np

# import matplotlib.pyplot as plt
# import sounddevice as sd
# import soundfile as sf


class node:
    def __init__(self, loc = int):
        self.loc = loc
        self.x = float
        self.y = float
        self.vis = float

    def updateNode(self, dic = {}):
        self.x = dic[self.loc]['x']
        self.y = dic[self.loc]['y']
        self.vis = dic[self.loc]['vis']


class extremity:
    def __init__(self, tail = int, head = int):
        
        # Tail and head of foot / hand vector, pointed outward from base of extremity
        self.tail = node(tail)
        self.head = node(head)

        self.angle = [] # Vector angle values
        self.angVel = [] # Angular velocity values
        self.vert = [] # Delta Y values
        self.dVert = [] # Change in delta Y (rel. velocity of head)

    def addAngle(self):
        
        # Distances relative to screen (i.e. 0.0 - 1.0) converted to absolute distances
        xDisp = capWidth * (self.head.x - self.tail.x)
        yDisp = capHeight * (self.head.y - self.tail.y)

        # Angle value normalized to degree range -180 : 180, w. origin shifted to floor
        theta = degrees(atan2(xDisp, yDisp))
        self.angle.append(theta)

        if len(self.angle) > 1:
            dTheta = self.angle[-1] - self.angle[-2]
            self.angVel.append(dTheta)

        # Update change in delta Y for vertical hit check
        self.vert.append(-1 * yDisp)
        if len(self.vert) > 1:
            deltaY = self.vert[-1] - self.vert[-2]
            self.dVert.append(deltaY)
            
        if len(self.dVert) > 3:
            self.angle.pop(0)
            self.angVel.pop(0)
            self.vert.pop(0)
            self.dVert.pop(0)


def PoseDetection():

    # Init mediapipe pose class
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    # FIXME mp_drawing_styles = mp.solutions.drawing_styles
    
    # Init video pose object
    vid_pose = mp_pose.Pose()
    
    #init landmark dictionary
    coordinate = dict.fromkeys(['x','y','z','vis'], None)
    dic = dict.fromkeys(range(33), coordinate)

    # Torso definitions
    leftShoulder = node(11)
    rightShoulder = node(12)
    leftHip = node(23)
    rightHip = node(24)

    torso = [leftShoulder, rightShoulder, leftHip, rightHip]

    # Limb definitions
    leftHand = extremity(15, 19)
    rightHand = extremity(16, 20)
    leftFoot = extremity(29, 31)
    rightFoot = extremity(30, 32)

    limbs = [leftHand, rightHand, leftFoot, rightFoot]
    
    # Audio dictionary
    sounds = {
        'Ride': "./Motion-Project/Drum Sounds/Samples/ride-acoustic01.wav",
        'Tom1': "./Motion-Project/Drum Sounds/Samples/tom-acoustic01.wav",
        'Tom2': "./Motion-Project/Drum Sounds/Samples/tom-acoustic02.wav",
        'Hat': "./Motion-Project/Drum Sounds/Samples/hihat-plain.wav",
        'HatOpen': "./Motion-Project/Drum Sounds/Samples/openhat-analog.wav",
        'Crash': "./Motion-Project/Drum Sounds/Samples/crash-acoustic.wav",
        'FTom': "./Motion-Project/Drum Sounds/Samples/tom-rototom.wav",
        'SD': "./Motion-Project/Drum Sounds/Samples/snare-acoustic01.wav",
        'BD': "./Motion-Project/Drum Sounds/Samples/kick-classic.wav",
        'On': './Motion-Project/Drum Sounds/Samples/clap-808.wav',
        'Off': './Motion-Project/Drum Sounds/Samples/cowbell-808.wav'
    }

    # Audio mapping grid
    soundCodes = [['On', 'Off'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]
    activeSound = False

    # Default border color
    borderColor = (0, 0, 255)
    

    # Main loop
    while True:

        # Read image
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (capWidth, capHeight))
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process image for body landmarks
        results = vid_pose.process(imgRGB)
        landmarks = results.pose_landmarks

        if landmarks == None:
            continue

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (255,0,255), thickness = 2, circle_radius = 1))

        # Get hand / foot landmarks
        for mark in range(33):

            data_point = landmarks.landmark[mark]
            dic[mark] = {
                'x': data_point.x,
                'y': data_point.y,
                'z': data_point.z,
                'vis': data_point.visibility}
    
        # Torso update / visibility check
        inFrame = True
        for item in torso:

            item.updateNode(dic)
            if item.vis < 0.5:
                inFrame = False
                

        # SoundCheck
        if inFrame == True:

            gridRows, gridColumns = updateGrid(torso)

            for item in limbs:

                # Update extremity vector locations, visibility
                item.tail.updateNode(dic)
                item.head.updateNode(dic)

                # Check for limb hit
                isHit = hitCheck(item)

                if isHit == True:

                    mapVal = map(item, gridRows, gridColumns, soundCodes)
                  
                    # Mapping adjustments
                    if mapVal == False:
                        break

                    elif mapVal == 'On':
                        activeSound = True
                        borderColor = (255, 0, 0)

                    elif mapVal == 'Off':
                        activeSound = False
                        borderColor = (0, 255, 0)
                        playsound(sounds[mapVal], block = False)

                    elif mapVal == 'Hat' and leftFoot.head.vis > 0.5 and abs(leftFoot.angle[-1]) > 90:
                        mapVal == 'HatOpen'
                  

                    # Play mapped Audio
                    if activeSound == True:
                        playsound(sounds[mapVal], block = False)

                    # TODO REFERENCE - Remove before deployment
                    print("hit", mapVal, item.dVert[-1])

        # Border initialization
        top = int(0.05 * frame.shape[0])  # shape[0] = rows
        bottom = top
        left = int(0.05 * frame.shape[1])  # shape[1] = cols
        right = left

        frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, None, borderColor)

        # Show frame
        cv2.imshow("Motion Cap", frame)

        # Press Q on keyboard to exit, else wait 3ms
        if cv2.waitKey(3) & False:
            break

        # Cancel when window closed
        if cv2.getWindowProperty('Motion Cap', cv2.WND_PROP_VISIBLE) < 1:
            break

    return limbs


def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average


def hitCheck(limb):

    visMin = 0.5 # Minimum visibility value for hit
    R = 15 # Downward angular velocity activation threshold (hands)
    T = -7 # Downward vertical velocity activation threshold
    minAngle = 10 # Min angle for angle check
    maxAngle = 150 # Max angle for angle check

    if limb.tail.vis < visMin and limb.head.vis < visMin:
        return False

    # Update limb angles
    limb.addAngle()

    if len(limb.dVert) < 2:
        return False

    # Prep hit check from extremity angle behavior
    a = limb.angle[-1]
    v1 = limb.angVel[-2]
    v2 = limb.angVel[-1]
    h1 = limb.dVert[-2]
    h2 = limb.dVert[-1]

    # Boolean Checks for hit criteria
    leftHit = minAngle < a < maxAngle and v1 < -R and v2 > (0.5 * v1) # Sudden minimum in angular velocity
    rightHit = (-1 * maxAngle) < a < minAngle and v1 > R and v2 < (0.5 * v1) # Sudden maximum in in angular velocity
    altHit = h1 < T and h2 > 0.5 * h1 # Sudden minimum in vertical velocity

    # if leftHit or rightHit or midHit:
    if leftHit or rightHit or altHit:
        return True
    else:
        return False


def updateGrid(torso):
# Calculate hit grid from torso points
# hitGrid: [['On', 'Off'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]

    # Reinitialize torso points
    leftShoulder = torso[0]
    rightShoulder = torso[1]
    leftHip = torso[2]
    rightHip = torso[3]

    # Calculate reference locations
    # TODO Explain grid in ReadMe
    waistY = avg(leftHip.y, rightHip.y)
    shoulderY = avg(leftShoulder.y, rightShoulder.y)
    torsoHalf = (waistY - shoulderY) / 2
    waistDisp = leftHip.x - rightHip.x
    midX = avg(leftHip.x, rightHip.x)

    # Calculate endpoints / midpoints of hit grid
    rowRanges = [0, shoulderY - torsoHalf, waistY - torsoHalf, waistY + torsoHalf, 1]
    colRanges = [[0, midX, 1], [0, rightShoulder.x - waistDisp, rightHip.x, leftHip.x, leftShoulder.x + waistDisp / 2, 1], [0, rightShoulder.x, leftHip.x, leftHip.x + waistDisp, 1], [0, midX, 1]]

    return rowRanges, colRanges


def map(extremity, rowRanges, colRanges, soundCodes):
    
    x = extremity.head.x
    y = extremity.head.y

    rowMap = int
    colMap = int

    if 0.05 < y < 0.15 and 0.05 < x < 0.15:
        return 'button'

    # Map Row, then Column of extremity head
    for i in range(len(rowRanges) - 1):
        if rowRanges[i] <= y <= rowRanges[i + 1]:
            rowMap = i
        elif y < 0 or y > 1:
            return False # For when hit triggered with extremity out of frame

    for j in range(len(colRanges[rowMap]) - 1):
        if colRanges[rowMap][j] <= x <= colRanges[rowMap][j + 1]:
            colMap = j
        elif x < 0 or x > 1:
            return False

    # Map to drum code
    mapVal = soundCodes[rowMap][colMap]

    return mapVal

def overlay(frame):
    cv2.rectangle(frame, (420, 205), (595, 385),
    (0, 0, 255), -1)
    cv2.putText(frame, "Player not fully in frame.", (windowWidth / 2, windowHeight / 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    cv2.rectangle(frame, (10,30), (60, 80), (0,0,0), -1)
    cv2.putText(frame, "On", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)

####################################################

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = int(cap.get(3)) #640
capHeight = int(cap.get(4)) #480

# Get active window size
root = tk.Tk()
windowWidth, windowHeight = root.winfo_screenwidth(), root.winfo_screenheight()

# Scale camera output value
a = windowWidth / capWidth
b = 1920 / 1440
scale = min((windowWidth / capWidth), (windowHeight / capHeight))
capWidth = int(capWidth * scale)
capHeight = int(capHeight * scale)

cv2.namedWindow("Motion Cap", cv2.WINDOW_NORMAL)
# cv2.moveWindow("Motion Cap", 480, 240)
cv2.resizeWindow("Motion Cap", windowWidth, windowHeight)

xGrid = []
yGrid = []

limbs = PoseDetection()

# for item in limbs:
#     plt.subplot(2,2,1)
#     plt.plot([x for x in range(len(item.angle))], item.angle, label = "angle")
#     plt.subplot(2,2,2)
#     plt.plot([x for x in range(len(item.angVel))], item.angVel, label = "theta")
#     plt.subplot(2,2,3)
#     plt.plot([x for x in range(len(item.vert))], item.vert, label = "vert")
#     plt.subplot(2,2,4)
#     plt.plot([x for x in range(len(item.dVert))], item.dVert, label = "dVert")

# plt.show()

cap.release()
cv2.destroyAllWindows()
