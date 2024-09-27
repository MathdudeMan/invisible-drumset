import cv2
import mediapipe as mp
from math import degrees, atan2
from playsound import playsound
import tkinter as tk

# Options for testing
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


class torso:
    def __init__(self, lShoulder, rShoulder, lHip, rHip):
        self.lShoulder = lShoulder
        self.rShoulder = rShoulder
        self.lHip = lHip
        self.rHip = rHip


class extremity:
    def __init__(self, tail = int, head = int, type = '', side = ''):
        
        self.type = type # Possible values 'Hand' and 'Foot'
        self.side = side # 'Right' or 'Left'

        # Tail and head of foot / hand vector, pointed outward from base of extremity
        self.tail = node(tail)
        self.head = node(head)

        self.angle = [] # Vector angle values
        self.angVel = [] # Angular velocity values
        self.vert = [] # Delta Y values
        self.dVert = [] # Change in delta Y (rel. velocity of head)

    def addAngle(self):
        
        # Distances relative to screen (i.e. 0.0 - 1.0) converted to absolute distances
        xDisp = windowWidth * (self.head.x - self.tail.x)
        yDisp = windowHeight * (self.head.y - self.tail.y)

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
        
        # Angle / delta-Y queue cleanup - comment out during data display 
        if len(self.angVel) > 3:
            self.angle.pop(0)
            self.angVel.pop(0)

        if len(self.dVert) > 3:
            self.vert.pop(0)
            self.dVert.pop(0)


class button:
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    
def main():
# Main Loop

    # Init mediapipe pose class
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # Init video pose object
    vid_pose = mp_pose.Pose()
    
    #init landmark dictionary
    coordinate = dict.fromkeys(['x','y','z','vis'], None)
    dataDict = dict.fromkeys(range(33), coordinate)

    # Torso definitions
    leftShoulder = node(11)
    rightShoulder = node(12)
    leftHip = node(23)
    rightHip = node(24)

    torso = [leftShoulder, rightShoulder, leftHip, rightHip]

    # Limb definitions
    leftHand = extremity(15, 17, 'Hand', 'Left')
    rightHand = extremity(16, 18, 'Hand', 'Right')
    leftFoot = extremity(29, 31, 'Foot', 'Left')
    rightFoot = extremity(30, 32, 'Foot', 'Right')

    extremities = [leftHand, rightHand, leftFoot, rightFoot]
    
    sounds = {
        'Ride': "./Motion-Project/assets/Used_Audio/ride-acoustic02.wav",
        'Tom1': "./Motion-Project/assets/Used_Audio/tom-acoustic01.wav",
        'Tom2': "./Motion-Project/assets/Used_Audio/tom-acoustic02.wav",
        'Hat': "./Motion-Project/assets/Used_Audio/hihat-acoustic01.wav",
        'HatOpen': "./Motion-Project/assets/Used_Audio/hihat-dist02.wav",
        'Crash': "./Motion-Project/assets/Used_Audio/crash-acoustic.wav",
        'FTom': "./Motion-Project/assets/Used_Audio/tom-rototom.wav",
        'SD': "./Motion-Project/assets/Used_Audio/snare-acoustic01.wav",
        'BD': "./Motion-Project/assets/Used_Audio/kick-classic.wav",
        'Special1': './Motion-Project/assets/Used_Audio/clap-808.wav',
        'Special2': './Motion-Project/assets/Used_Audio/cowbell-808.wav',
        'Off': './Motion-Project/assets/Used_Audio/Cowbell.wav',
        'On': './Motion-Project/assets/Used_Audio/Cowbell.wav'
    }

    # Audio mapping grid
    soundCodes = [['Special1', 'Special2'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]
    
    # State triggers for enabling sound output and UI changes
    inFrame = False
    activeSound = False
    UIState = 'Out'

    # Declare button and x, y ranges within frame
    powButton = button(0.025, 0.25, 0.025, 0.25)

    # Button text location parameters
    powX = 0.045
    powY = 0.125
    altX = 0.045
    altY = 0.185

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

        # Process image and set parameters
        frame = cv2.resize(frame, (windowWidth, windowHeight))
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get body landmarks from image
        results = vid_pose.process(imgRGB)
        rawData = results.pose_landmarks # Returned as a class of landmarks

        if rawData == None:
            continue

        print(frame.height, frame.width)

        # Store hand / foot landmarks
        for mark in range(33):

            markCoord = rawData.landmark[mark]
            dataDict[mark] = {
                'x': markCoord.x,
                'y': markCoord.y,
                # 'z': data_point.z,
                'vis': markCoord.visibility}

        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 1))

        # Flip annotated image horizontally, output mirrors player
        frame = cv2.flip(frame, 1)
    

        # Update torso, check if all 4 nodes are in frame
        inFrame = True
        for point in torso:

            point.updateNode(dataDict)

            if point.vis < 0.5:
                inFrame = False

        # Hit checks when user is in frame
        if inFrame == True:

            # Update sound grid
            gridRows, gridColumns = updateGrid(torso)

            # Sound Check / Output for each extremity
            for object in extremities:

                # Update extremity vector parameters
                object.tail.updateNode(dataDict)
                object.head.updateNode(dataDict)

                # Check for drum hit
                isHit = hitCheck(object)

                # Play sound when hit occurs
                if isHit == True:

                    # Get drum mapping
                    mapVal = map(object, gridRows, gridColumns, powButton, soundCodes)
                  
                    # Check for false positive from out-of-frame extremity
                    if mapVal == False:
                        continue

                    # Open Hi Hat when left foot angled upwards
                    elif mapVal == 'Hat' and extremities[2].head.vis > 0.5 and abs(extremities[2].angle[-1]) > 70:
                        mapVal = 'HatOpen'

                    # Button trigger
                    elif mapVal == 'Button':
                        if activeSound == True:
                            activeSound = False
                            playsound(sounds['Off'], block = False)
                            continue
                        else:
                            activeSound = True
                            mapVal = 'On'

                    # Play mapped Audio when sound setting on
                    if activeSound == True:
                        playsound(sounds[mapVal], block = False)

                    # FIXME
                    print("hit " + mapVal)

            # Declare resultant state of program
            if activeSound == True:
                UIState = 'On'
            else: # activeSound == False, but inFrame
                UIState = 'Off'

        # When user out of frame
        else:

            activeSound = False
            UIState = 'Out'

            # Draw "Invisible Drum_Kit" Title
            frame = cv2.putText(frame, "Invisible Drum Kit", (int(0.35 * windowWidth), int(0.1 * windowHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 4, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)
            frame = cv2.putText(frame, "Inspired by Rowan Atkinson", (int(0.4 * windowWidth), int(0.15 * windowHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 2, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

            # Draw "Full Body Not in Frame" Message
            tL = (int(0.2 * windowWidth), int(0.85 * windowHeight))
            bR = (int(0.8 * windowWidth), int(0.95 * windowHeight))
            frame = cv2.rectangle(frame, tL, bR, color = (0,0,200), thickness = -1)
            
            frame = cv2.putText(frame, "Full Body Not In Frame", (int(0.212 * windowWidth), int(0.925 * windowHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 3, color = (255,255,255), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)


        # Set button / border parameters
        match UIState:
            case 'On':
                borderColor = (0, 255, 0)
                stateText = "Power: ON"
                altText = "(Hit Here to Switch)"
                btnBG = (20,20,20)
                btnTxtColor = (240, 240, 255)
            case 'Off':
                borderColor = (0, 0, 255)            
                stateText = "Power: OFF"
                altText = "(Hit Here to Switch)"
                btnBG = (80,80,80)
                btnTxtColor = (200, 200, 255)
            case 'Out':
                borderColor = (50, 90, 0)
                stateText = "Power: OFF"
                altText = "(Enter Frame to Use)"
                btnBG = (60,60,60)
                btnTxtColor = (150, 150, 150)  
        


        
        # Draw On/Off Button
        tL = (int(powButton.x1 * windowWidth), int(powButton.y1 * windowHeight))
        bR = (int(powButton.x2 * windowWidth), int(powButton.y2 * windowHeight))
        frame = cv2.rectangle(frame, tL, bR, color = btnBG, thickness = -1)

        frame = cv2.putText(frame, stateText, (int(powX * windowWidth), int(powY * windowHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 2, color = btnTxtColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

        frame = cv2.putText(frame, altText, (int(altX * windowWidth), int(altY * windowHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 1, color = btnTxtColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

        # Draw border
        top = int(0.05 * windowHeight)
        bottom = top
        left = int(0.05 * windowWidth)
        right = left
        frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, None, borderColor)


        # Display frame
        cv2.imshow('Motion Cap', frame)

        # Frame buffer (Conditional always False)
        if cv2.waitKey(2) == -2:
            pass

        # End loop when when window closed
        if cv2.getWindowProperty('Motion Cap', cv2.WND_PROP_VISIBLE) < 1:
            break

    # Return extremities array for testing full-run data
    return extremities


def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average


def updateGrid(torso):
    """This is cool.

    69 nice
    
    """


# Calculate hit grid from torso points
# hitGrid: [['Special1', 'Special2'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'Hat']]

    # Reinitialize torso points
    leftShoulder = torso[0]
    rightShoulder = torso[1]
    leftHip = torso[2]
    rightHip = torso[3]

    # Vertical references
    waistY = avg(leftHip.y, rightHip.y)
    shoulderY = avg(leftShoulder.y, rightShoulder.y)
    torsoSplitY = (1/3) * (waistY - shoulderY)

    # Horizontal references
    waistDisp = leftHip.x - rightHip.x
    torsoSplitX = avg(leftHip.x, rightHip.x)

    # Calculate rows endpoints, from Top to Bottom
    rowRanges = [0, shoulderY - torsoSplitY, waistY - torsoSplitY, waistY + torsoSplitY, 1]
    
    # Calculate sub-column endpoints by Row, Top to Bottom and Right to Left (due to image flip)
    colRanges = [[0, torsoSplitX, 1], 
                 [0, rightShoulder.x - waistDisp, rightShoulder.x, torsoSplitX, leftShoulder.x + waistDisp, 1], 
                 [0, rightShoulder.x, leftShoulder.x, leftShoulder.x + waistDisp, 1], 
                 [0, torsoSplitX, 1]]

    return rowRanges, colRanges


def hitCheck(extremity):

    # Calibration variables
    visMin = 0.5 # Minimum visibility value for hit

    wLim = 20 # Downward angular velocity activation threshold (for hands)
    vLim = -10 # Downward vertical velocity activation threshold

    minAngle = 20 # Min angle for angle check
    maxAngle = 150 # Max angle for hand angle check
    midMin = 80 # Allow vert check for midrange hand hits
    midMax = 100

    anglSwap = 300 # Min angle change to detect sign change (e.g. + to -)

    # Prevent false positives from out-of-frame extremities
    if extremity.tail.vis < visMin and extremity.head.vis < visMin:
        return False

    # Update extremity angles
    extremity.addAngle()

    # Prevent indexError
    if len(extremity.dVert) < 2:
        return False

    # Pull extremity angle behavior for hit check calculations
    a = extremity.angle[-1]
    w1 = extremity.angVel[-2]
    w2 = extremity.angVel[-1]
    v1 = extremity.dVert[-2]
    v2 = extremity.dVert[-1]

    # Detect angle sign change
    if abs(w2) > anglSwap:
        extremity.angVel.pop(-1)
        return False

    # Criteria for enabling Vertical Velocity check
    if extremity.type == 'Hand':
        alt = (abs(a) < minAngle or abs(a) > maxAngle or midMin < abs(a) < midMax) 
    elif extremity.type == 'Foot':
        alt = True

    # Boolean Checks for hit criteria
    leftHit = minAngle < a < maxAngle and w1 < -wLim and w2 > (0.5 * w1) # Sharp minimum in angular velocity
    rightHit = (-1 * maxAngle) < a < (-1 * minAngle) and w1 > wLim and w2 < (0.5 * w1) # Sharp maximum in angular velocity
    altHit = alt and v1 < vLim and v2 > 0.3 * v1 # Sharp minimum in vertical velocity

    return leftHit or rightHit or altHit


def map(extremity, rowRanges, colRanges, powerB, soundCodes):
    """Determine map location of limb for sound output
    
    Keyword arguments:
    extremity -- 
    """

    x = extremity.head.x
    y = extremity.head.y

    # Prevent leakage of out-of-frame hit triggers
    if not (0 <= x <= 1 and 0 <= y <= 1):
        return False

    # Auto-map feet
    if extremity.type == 'Foot' and extremity.side == 'Left':
        return 'Hat'
    elif extremity.type == 'Foot' and extremity.side == 'Right':
        return 'BD'

    rowMap = int
    colMap = int

    # Check for button hit assuming image flipped horizontally
    if (1 - powerB.x1) > x > (1 - powerB.x2) and powerB.y1 < y < powerB.y2:
        return 'Button'

    # Map Row, then Column of extremity head
    for i in range(len(rowRanges) - 1):
        if rowRanges[i] <= y <= rowRanges[i + 1]:
            rowMap = i

    for j in range(len(colRanges[rowMap]) - 1):
        if colRanges[rowMap][j] <= x <= colRanges[rowMap][j + 1]:
            colMap = j
        
    # Convert grid location to drum code
    mapVal = soundCodes[rowMap][colMap]

    return mapVal

####################################################

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = int(cap.get(3)) #640
capHeight = int(cap.get(4)) #480

# Get active screen size (1920 x 1080)
root = tk.Tk()
screenWidth, screenHeight = int(root.winfo_screenwidth()), int(root.winfo_screenheight())

# Scale camera output size so both parameters fill screen
scale = max((screenWidth / capWidth), (screenHeight / capHeight))
windowWidth = int(capWidth * scale) #1920
windowHeight = int(capHeight * scale) #1440

# Define fullscreen desktop window (cv2 autoshrinks so frame ratio kept)
cv2.namedWindow("Motion Cap", cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow("Motion Cap", windowWidth, windowHeight)

# Main function loop
extremities = main()

# Uncomment to graph extremity behavior
# for item in extremities:
#     plt.subplot(2,2,1)
#     plt.plot([x for x in range(len(item.angle))], item.angle, label = "angle")
#     plt.subplot(2,2,2)
#     plt.plot([x for x in range(len(item.angVel))], item.angVel, label = "theta")
#     plt.subplot(2,2,3)
#     plt.plot([x for x in range(len(item.vert))], item.vert, label = "vert")
#     plt.subplot(2,2,4)
#     plt.plot([x for x in range(len(item.dVert))], item.dVert, label = "dVert")

plt.show()

cap.release()
cv2.destroyAllWindows()
