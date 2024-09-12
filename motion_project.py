import cv2
import mediapipe as mp
from math import degrees, atan2
from playsound import playsound
import tkinter as tk

import matplotlib.pyplot as plt
# import sounddevice as sd
# import soundfile as sf
# import pygame.mixer as pg


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
    def __init__(self, tail = int, head = int, type = ''):
        
        self.type = type # Possible values 'Hand' and 'Foot'

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
            
        # if len(self.dVert) > 3:
        #     self.angle.pop(0)
        #     self.angVel.pop(0)
        #     self.vert.pop(0)
        #     self.dVert.pop(0)


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
    leftHand = extremity(15, 17, 'Hand')
    rightHand = extremity(16, 18, 'Hand')
    leftFoot = extremity(29, 31, 'Foot')
    rightFoot = extremity(30, 32, 'Foot')

    limbs = [leftHand, rightHand, leftFoot, rightFoot]
    
    sounds = {
        'Ride': "./Motion-Project/Used_Audio/ride-acoustic01.wav",
        'Tom1': "./Motion-Project/Used_Audio/tom-acoustic01.wav",
        'Tom2': "./Motion-Project/Used_Audio/tom-acoustic02.wav",
        'Hat': "./Motion-Project/Used_Audio/hihat-plain.wav",
        'HatOpen': "./Motion-Project/Used_Audio/openhat-analog.wav",
        'Crash': "./Motion-Project/Used_Audio/crash-acoustic.wav",
        'FTom': "./Motion-Project/Used_Audio/tom-rototom.wav",
        'SD': "./Motion-Project/Used_Audio/snare-acoustic01.wav",
        'BD': "./Motion-Project/Used_Audio/kick-classic.wav",
        'Special1': './Motion-Project/Used_Audio/clap-808.wav',
        'Special2': './Motion-Project/Used_Audio/cowbell-808.wav',
        'Off': './Motion-Project/Used_Audio/Cowbell.wav',
        'On': './Motion-Project/Used_Audio/Cowbell.wav'
    }

    # Audio mapping grid
    soundCodes = [['Special1', 'Special2'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]
    activeSound = False

    # UI Variable declarations
    borderColor = (0,0,0)
    stateText = ""
    altText = ""
    btnBG = (0,0,0)
    btnTxtColor = (0,0,0)
    

    # Main loop
    while True:

        # Read image
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (capWidth, capHeight))
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        height = frame.shape[0]
        width = frame.shape[1]

        # Process image for body landmarks
        results = vid_pose.process(imgRGB)
        landmarks = results.pose_landmarks

        if landmarks == None:
            continue

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (0,255,0 ), thickness = 2, circle_radius = 1))

        # Store hand / foot landmark,
        for mark in range(33):

            data_point = landmarks.landmark[mark]
            dic[mark] = {
                'x': data_point.x,
                'y': data_point.y,
                'z': data_point.z,
                'vis': data_point.visibility}
            
        # Flip frame to mirror player
        frame = cv2.flip(frame, 1)
    
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

                # FIXME Reorder this
                if isHit == True:

                    mapVal = map(item, gridRows, gridColumns, soundCodes)
                  
                    # Mapping adjustments
                    if mapVal == False:
                        break

                    elif mapVal == 'Button':
                        if activeSound == True:
                            activeSound = False
                            playsound(sounds['Off'], block = False)
                        else:
                            activeSound = True
                            mapVal = 'On'

                    elif mapVal == 'Hat' and leftFoot.head.vis > 0.5 and abs(leftFoot.angle[-1]) > 90:
                        mapVal == 'HatOpen'
                  
                    # Play mapped Audio
                    if activeSound == True:
                        playsound(sounds[mapVal], block = False)


                    # FIXME REFERENCE - Remove before deployment
                    print("hit", mapVal, item.dVert[-1])


                # Set inFrame drawing parameters
                if activeSound == True:
                    borderColor = (0, 255, 0)
                    stateText = "Power: ON"
                    altText = "(Hit Here to Switch)"
                    btnBG = (20,20,20)
                    btnTxtColor = (240, 240, 255)
                else:
                    borderColor = (0, 0, 255)            
                    stateText = "Power: OFF"
                    altText = "(Hit Here to Switch)"
                    btnBG = (80,80,80)
                    btnTxtColor = (200, 200, 255)


        else: # inFrame == False

            activeSound = False

            # Set notInFrame drawing parameters
            borderColor = (50, 90, 0)
            stateText = "Power: OFF"
            altText = "(Enter Frame to Use)"
            btnBG = (60,60,60)
            btnTxtColor = (150, 150, 150)       

            # "Invisible Drum_Kit" Title
            frame = cv2.putText(frame, "Invisible Drum Kit", (int(0.35 * width), int(0.1 * height)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 4, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)
            frame = cv2.putText(frame, "Inspired by Rowan Atkinson", (int(0.4 * width), int(0.15 * height)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 2, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

            # "Full Body Not in Frame" Message
            tL = (int(0.2 * width), int(0.85 * height))
            bR = (int(0.8 * width), int(0.95 * height))
            frame = cv2.rectangle(frame, tL, bR, color = (0,0,200), thickness = -1)
            
            frame = cv2.putText(frame, "Full Body Not In Frame", (int(0.212 * width), int(0.925 * height)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 3, color = (255,255,255), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)


        # Draw On/Off Button
        tL = (int(0.025 * width), int(0.025 * height))
        bR = (int(0.25 * width), int(0.15 * height))
        frame = cv2.rectangle(frame, tL, bR, color = btnBG, thickness = -1)

        frame = cv2.putText(frame, stateText, (int(0.045 * width), int(0.08 * height)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 2, color = btnTxtColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

        frame = cv2.putText(frame, altText, (int(0.045 * width), int(0.12 * height)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 1, color = btnTxtColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

        # Border initialization
        top = int(0.05 * height)
        bottom = top
        left = int(0.05 * width)
        right = left
        frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, None, borderColor)

        # Show frame
        cv2.imshow('Motion Cap', frame)

        # Wait 3ms
        if cv2.waitKey(2) == -2:
            break

        # Cancel when window closed
        if cv2.getWindowProperty('Motion Cap', cv2.WND_PROP_VISIBLE) < 1:
            break

    return limbs


def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average


def updateGrid(torso):
# Calculate hit grid from torso points
# hitGrid: [['Special1', 'Special2'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]

    # Reinitialize torso points
    leftShoulder = torso[0]
    rightShoulder = torso[1]
    leftHip = torso[2]
    rightHip = torso[3]

    # Reference Y Values
    waistY = avg(leftHip.y, rightHip.y)
    shoulderY = avg(leftShoulder.y, rightShoulder.y)
    torsoSplit = (waistY - shoulderY) / 3

    # Reference X Valuess
    waistDisp = leftHip.x - rightHip.x
    midX = avg(leftHip.x, rightHip.x)

    # Calculate endpoints / midpoints of hit grid
    # Rows, Top to Bottom
    rowRanges = [0, shoulderY - torsoSplit, waistY - torsoSplit, waistY + torsoSplit, 1]
    
    # Sub-columns by Row, Right to Left
    colRanges = [[0, midX, 1], 
                 [0, rightShoulder.x - waistDisp, rightHip.x, leftShoulder.x, leftShoulder.x + waistDisp, 1], 
                 [0, rightShoulder.x, leftShoulder.x, leftShoulder.x + waistDisp, 1], 
                 [0, midX, 1]]

    return rowRanges, colRanges


def hitCheck(limb):

    visMin = 0.5 # Minimum visibility value for hit
    wLim = 20 # Downward angular velocity activation threshold (for hands)
    vLim = -7 # Downward vertical velocity activation threshold
    minAngle = 20 # Min angle for angle check
    maxAngle = 160 # Max angle for angle check

    # Prevent hit from out-of-frame extremities
    if limb.tail.vis < visMin and limb.head.vis < visMin:
        return False

    # Update limb angles
    limb.addAngle()

    # Prevent indexError
    if len(limb.dVert) < 2:
        return False

    # Locate extremity angle behavior for hit check calculations
    a = limb.angle[-1]
    w1 = limb.angVel[-2]
    w2 = limb.angVel[-1]
    v1 = limb.dVert[-2]
    v2 = limb.dVert[-1]

    # Protects from false positives due to axis crossing
    if abs(w1) > 330 or abs(w2) > 330:
        return False

    # Criteria for Vertical Velocity check
    if limb.type == 'Hand':
        alt = (abs(a) < minAngle or abs(a) > maxAngle or 85 < abs(a) < 95) 
    elif limb.type == 'Foot':
        alt = True

    # Boolean Checks for hit criteria
    leftHit = minAngle < a < maxAngle and w1 < -wLim and w2 > (0.5 * w1) # Sharp minimum in angular velocity
    rightHit = (-1 * maxAngle) < a < (-1 * minAngle) and w1 > wLim and w2 < (0.5 * w1) # Sharp maximum in angular velocity
    altHit = alt and v1 < vLim and v2 > 0.5 * v1 # Sharp minimum in vertical velocity

    if leftHit or rightHit or altHit:
        return True
    else:
        return False


def map(extremity, rowRanges, colRanges, soundCodes):
    
    x = extremity.head.x
    y = extremity.head.y

    rowMap = int
    colMap = int

    # if 0.025 < x < 0.25 and 0.025 < y < 0.15:
    #     return 'Button'
    
    if 0.75 < x < 0.975 and 0.025 < y < 0.15:
        return 'Button'

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

    # Map location to drum code
    mapVal = soundCodes[rowMap][colMap]

    return mapVal

####################################################

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = int(cap.get(3)) #640
capHeight = int(cap.get(4)) #480

# Get active window size
root = tk.Tk()
windowWidth, windowHeight = int(root.winfo_screenwidth()), int(root.winfo_screenheight())

# Scale camera output value
scale = max((windowWidth / capWidth), (windowHeight / capHeight))
capWidth = int(capWidth * scale)
capHeight = int(capHeight * scale)

cv2.namedWindow("Motion Cap", cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow("Motion Cap", capWidth, capHeight)

xGrid = []
yGrid = []

limbs = PoseDetection()

# FIXME Extremity behavior testing
for item in limbs:
    plt.subplot(2,2,1)
    plt.plot([x for x in range(len(item.angle))], item.angle, label = "angle")
    plt.subplot(2,2,2)
    plt.plot([x for x in range(len(item.angVel))], item.angVel, label = "theta")
    plt.subplot(2,2,3)
    plt.plot([x for x in range(len(item.vert))], item.vert, label = "vert")
    plt.subplot(2,2,4)
    plt.plot([x for x in range(len(item.dVert))], item.dVert, label = "dVert")

plt.show()

cap.release()
cv2.destroyAllWindows()
