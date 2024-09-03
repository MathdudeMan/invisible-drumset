import cv2
import mediapipe as mp
from math import degrees, atan2
import matplotlib.pyplot as plt
from playsound import playsound


class node:
    def __init__(self, loc = int):
        self.loc = loc
        self.x = float
        self.y = float
        self.vis = float

# class headNode(node):
#   def __init__(self, loc = int):  
#       self.yVel = [int]


class extremity:
    def __init__(self, tail = int, head = int):
        
        # Tail and head of foot / hand vector, pointed outward from base of extremity
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

        # if len(self.angVel) > 3:
        #     self.angle.pop()
        #     self.angVel.pop()


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

    activeSound = False

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

        if landmarks == None:
            continue

        # Get hand / foot landmarks
        for mark in range(33):

            data_point = landmarks.landmark[mark]

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

            gridRows, gridColumns = updateGrid(torso)

            for item in limbs:

                # Update extremity vector locations, visibility
                updateNode(item.tail, dic)
                # FIXME limb.head.vel.append(dic[limb.head]['y'] - limb.head.y)
                updateNode(item.head, dic)

                # Check for limb hit
                isHit = hitCheck(item)

                # FIXME Prototype
                activeSound = True

                if isHit == True:

                    mapVal = map(item, gridRows, gridColumns)
                  
                    # Mapping adjustments
                    if mapVal == False:
                        break

                    elif mapVal == 'On':
                        activeSound = True

                    elif mapVal == 'Off':
                        activeSound = False
                        audio(mapVal)

                    elif mapVal == 'Hat' and leftFoot.head.vis > 0.5 and abs(leftFoot.angle[-1]) > 90:
                        mapVal == 'HatOpen'
                  
                    # Play associated Audio
                    if activeSound == True:
                        audio(mapVal)

                    # TODO remove for reference
                    print("hit", len(item.angle), mapVal)

                # FIXME item.head.vel.pop()
                # item.angle.pop()

        # Press Q on keyboard to exit, else wait 3ms
        if cv2.waitKey(3) & 0xFF == ord('q'):
            break

    return limbs


def updateGrid(torso):
# Calculate hit grid from torso points

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

    # Grid range calculations
    rowRanges = [0, shoulderY - torsoHalf, waistY - torsoHalf, waistY + torsoHalf, 1]
    colRanges = [[0, midX, 1], [0, rightShoulder.x - waistDisp, rightHip.x, leftHip.x, leftShoulder.x + waistDisp / 2, 1], [0, rightShoulder.x, leftHip.x, leftHip.x + waistDisp, 1], [0, midX, 1]]

    return rowRanges, colRanges


def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average


def updateNode(node, dic = {}):
# Update values of a node from results dictionary

    node.x = dic[node.loc]['x']
    node.y = dic[node.loc]['y']
    node.vis = dic[node.loc]['vis']


def hitCheck(limb):

    visMin = 0.5 # Minimum visibility value for hit
    R = 15 # Downward angular velocity activation threshold

    if limb.tail.vis < visMin and limb.head.vis < visMin:
        return False

    # Update limb angles
    limb.addAngle()

    if len(limb.angVel) < 2:
        return False

    # Prep hit check from extremity angle behavior
    a = limb.angle[-1]
    v1 = limb.angVel[-2]
    v2 = limb.angVel[-1]
    # FIXME h1 = limb.head.vel[-1]
    # h2 = limb.head.vel[-2]

    # Boolean Checks for hit criteria
    rightHit = a > 0 and v1 > R and 0.5*v1 > v2
    leftHit = a < 0 and v1 < -R and 0.5*v1 < v2
    # FIXME midHit = (abs(a) < 10 or abs(a) > 170) and h1 < R and 0.5*h1 > h2

    if leftHit or rightHit: # or midHit
        return True
    else:
        return False


def map(extremity, rowRanges, colRanges):
    
    x = extremity.head.x
    y = extremity.head.y

    rowMap = int
    colMap = int

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
    soundCodes = [['On', 'Off'], ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], ['FTom', 'SD', 'Hat', 'Crash'], ['BD', 'HatPed']]

    mapVal = soundCodes[rowMap][colMap]

    return mapVal


def audio(mapNum):

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

    playsound(sounds[mapNum], block = False)


####################################################

# Activate Video / Webcam
cap = cv2.VideoCapture(0)
capWidth = cap.get(3) #640
capHeight = cap.get(4) #480

windowWidth = 800
windowHeight = 600

xGrid = []
yGrid = []

limbs = PoseDetection()

for limb in limbs:
    plt.subplot(1,2,1)
    plt.plot([x for x in range(len(limb.angle))], limb.angle, label = "angle")
    plt.subplot(1,2,2)
    plt.plot([x for x in range(len(limb.angVel))], limb.angVel, label = "theta")

plt.show()

cap.release()
cv2.destroyAllWindows()
