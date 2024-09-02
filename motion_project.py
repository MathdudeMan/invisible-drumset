import cv2
import mediapipe as mp
from math import degrees, atan2
import matplotlib.pyplot as plt
from playsound import playsound


class node:
    def __init__(self, loc = int):
        self.loc = loc
        self.x = int
        self.y = int
        self.vis = int

# class headNode(node):
#   def __init__(self, loc = int):  
#       self.yVel = [int]


class extremity:
    def __init__(self, tail = int, head = int):
        
        # # Tail and head of foot / hand vector, pointed outward from base of extremity
        self.tail = node(tail)
        self.head = node(head)

        self.angle = [] #Vector angle values
        self.angVel = [] #Angular velocity values

    def addAngle(self):
        
        # Relative positional differences (i.e. 0.0 - 1.0) converted to absolute values
        deltaX = capWidth * (self.head.x - self.tail.x)
        deltaY = capHeight * (self.head.y - self.tail.y)

        #Angle value normalized to degree range -180 : 180, w. origin shifted to floor
        theta = degrees(atan2(deltaY, deltaX)) + 90
        self.angle.append(theta)

        if len(self.angle) > 1:
            change = self.angle[-1] - self.angle[-2]
            self.angVel.append(change)


def PoseDetection():

    # Init mediapipe pose class
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    # FIXME mp_drawing_styles = mp.solutions.drawing_styles

    # Init video pose object
    vid_pose = mp_pose.Pose()

    # Loading image
    loading = cv2.imread('Motion-Project/icon.png')
    loading = cv2.resize(loading, (windowWidth, windowHeight))

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
    leftHand = extremity(15,19)
    rightHand = extremity(16,20)
    leftFoot = extremity(29,31)
    rightFoot = extremity(30,32)

    limbs = [leftHand, rightHand, leftFoot, rightFoot]

    # Main loop
    while True:

        # Read & process image
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (windowWidth, windowHeight))
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = vid_pose.process(imgRGB)

        # Read all landmarks
        landmarks = results.pose_landmarks

        # Get hand / foot landmarks
        for mark in range(33):

            data_point = landmarks.landmark[mark]

            if data_point == None:
                continue

            dic[mark] = {
                'x': data_point.x,
                'y': data_point.y,
                'z': data_point.z,
                'vis': data_point.visibility}
    
        # Torso update
        inFrame = True

        for item in torso:

            updateNode(item, dic)

            # Torso visibility check
            if item.vis < 0.5:
                inFrame = False
        
        if inFrame == False:

            cv2.imshow("Motion Cap", loading)

        else:

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), connection_drawing_spec = mp_drawing.DrawingSpec(color = (255,0,255), thickness = 2, circle_radius = 1))

            # Show frame
            cv2.imshow("Motion Cap", frame)

            # TODO initialize Grid
            rows, columns = updateGrid(torso)

            for item in limbs:

                # Update extremity vector locations, visibility
                updateNode(item.tail, dic)
                # FIXME limb.head.vel.append(dic[limb.head]['y'] - limb.head.y)
                updateNode(item.head, dic)

                hitCheck(item)
                # if hitCheck == True:
                #   mapNum = map2(item)
                #   mapNum arguments
                #   Get sound file from mapNum
                #   audio(mapNum)


                # FIXME limb.head.vel.pop()

        # Press Q on keyboard to exit, else wait 3ms
        if cv2.waitKey(3) & 0xFF == ord('q'):
            break

    return limbs


def updateGrid(torso):
    # Calculate hit grid from torso points

    leftShoulder = torso(1)
    rightShoulder = torso(2)
    leftHip = torso(3)
    rightHip = torso(4)

    waistY = avg(leftHip.y, rightHip.y)
    shoulderY = avg(leftShoulder.y, rightShoulder.y)
    midY = avg(waistY, shoulderY)
    waist = leftHip.x - rightHip.x
    midX = avg(leftHip.x, rightHip.x)

    yGrid = [0, shoulderY - midY, waistY - midY, waistY + midY, 1]
    xGrid = [[0, midX, 1], [0, rightShoulder.x, leftHip.x, leftHip.x + waist, 1], [0, rightShoulder.x + waist/2, rightHip.x, leftHip.x, leftShoulder.x + waist/2, 1], [0, midX, 1]]

    return yGrid, xGrid

def avg(x, y):

    average = (x + y) / 2
    return average


def updateNode(node, dic = {}):

    node.x = dic[node.loc]['x']
    node.y = dic[node.loc]['y']
    node.vis = dic[node.loc]['vis']


def hitCheck(limb):

    visMin = 0.5 # Minimum visibility value for hit
    R = 10 # Downward angular velocity activation threshold

    if limb.tail.vis < visMin and limb.head.vis < visMin:
        return

    # Update limb angles
    limb.addAngle()

    if len(limb.angVel) < 2:
        return

    # Prep hit check from extremity angle behavior
    a = limb.angle[-1]
    v1 = limb.angVel[-2]
    v2 = limb.angVel[-1]
    # FIXME h1 = limb.head.vel[-1]
    # h2 = limb.head.vel[-2]

    # Boolean Checks
    rightHit = a > 0 and v1 > R and 0.5*v1 > v2
    leftHit = a < 0 and v1 < -R and 0.5*v1 < v2
    # FIXME midHit = (abs(a) < 10 or abs(a) > 170) and h1 < R and 0.5*h1 > h2

    if leftHit or rightHit: # or midHit
        
        mapNum = map(limb)

        print("hit", len(limb.angle), mapNum, limb.head.vis)
            
        # if mapNum == 'On':
        #     playsound(Windows Startup)
        #   active = True
        # elif mapNum =='Off':
        #   playsound(Windows Shutdown)   
        #   active = False

        # if mapNum == 'Hat':
        #    if leftFoot.headVis > 0.5 and abs(leftFoot.angle[-1]) > 90:
        #           mapNum == 'HatOpen'

        # if active == True:
        audio(mapNum)

    return


def map(limb):
    # Determine region of appendage, indexed 1 - 16 in 4x4 grid from top left corner
    
    # Sound grid ranges
    hitGrid = [[0,0.3,0.5,0.65,1], [0,0.25,0.5,0.75,1]]

    mapNum = 0

    x = limb.head.x
    y = limb.head.y
    
    # x Check
    if x < hitGrid[0][1]:
        mapNum += 1
    elif x < hitGrid[0][2]:
        mapNum += 2
    elif x < hitGrid[0][3]:
        mapNum += 3
    else:
        mapNum += 4

    # y Check
    if y < hitGrid[1][1]:
        pass
    elif y < hitGrid[1][2]:
        mapNum += 4
    elif y < hitGrid[1][3]:
        mapNum += 8
    else:
        mapNum += 12

    # Open Hi Hat Check
    # if mapNum == 7 and leftFoot.headVis > 0.5 and abs(leftFoot.angle[-1]) > 90:
    #     mapNum = 17

    return mapNum


def map2(extremity, xGrid, yGrid):
    
    x = extremity.head.x
    y = extremity.head.y

    xMap = int
    yMap = int

    # Map Row, then Column of extremity head
    for i in range(len(yGrid) - 1):
        if yGrid[i] <= y <= yGrid[i + 1]:
            yMap = i

    for j in range(len(xGrid(yMap) - 1)):
        if xGrid[j] <= x <= xGrid[j + 1]:
            xMap = j

    # Map to drum code
    soundCodes = [['On', 'Off'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'CC'], ['BD', 'HatPed']]

    mapVar = soundCodes(yMap(xMap))

    return mapVar


def audio(mapNum):

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
        16: "./Motion-Project/Drum Sounds/Samples/kick-gritty.wav",
        17: "./Motion-Project/Drum Sounds/Samples/openhat-tight.wav"
    }

    # sounds = {
    #     'Ride': "./Motion-Project/Drum Sounds/Samples/ride-acoustic01.wav",
    #     'Tom1': "./Motion-Project/Drum Sounds/Samples/tom-acoustic01.wav",
    #     'Tom2': "./Motion-Project/Drum Sounds/Samples/tom-acoustic02.wav",
    #     'Hat': "./Motion-Project/Drum Sounds/Samples/hihat-plain.wav",
    #     'HatOpen': "./Motion-Project/Drum Sounds/Samples/openhat-analog.wav",
    #     'Crash': "./Motion-Project/Drum Sounds/Samples/crash-acoustic.wav",
    #     'FTom': "./Motion-Project/Drum Sounds/Samples/tom-rototom.wav",
    #     'SD': "./Motion-Project/Drum Sounds/Samples/snare-acoustic01.wav",
    #     'BD': "./Motion-Project/Drum Sounds/Samples/kick-classic.wav"
    # }

    playsound(sounds[mapNum], block = False)


####################################################

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = cap.get(3) #640
capHeight = cap.get(4) #480

windowWidth = 800
windowHeight = 600

limbs = PoseDetection()

for limb in limbs:
    plt.subplot(1,2,1)
    plt.plot([x for x in range(len(limb.angle))], limb.angle, label = "angle")
    plt.subplot(1,2,2)
    plt.plot([x for x in range(len(limb.angVel))], limb.angVel, label = "theta")

plt.show()

cap.release()
cv2.destroyAllWindows()
