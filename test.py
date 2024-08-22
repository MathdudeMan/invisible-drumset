import pygame
import math
#import pyglet

class extremity:
    def __init__(self, tail = int, head = int):
        self.tail = tail
        self.tailX = int
        self.tailY = int

        self.head = head
        self.headX = int
        self.headY = int

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

    pass

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
        for mark, data_point in zip(range(0,32), landmarks.landmark):
            dic[mark].update(
                x = data_point.x,
                y = data_point.y,
                z = data_point.z,
                vis = data_point.visibility)

        for item in limbs:
            hitCheck(item)

        # Press Q on keyboard to exit, else wait 1ms
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return landmarks


def hitCheck(limb):

    item.tailX = dic[item.tail]['x']
    item.tailY = dic[item.tail]['y']
    item.headX = dic[item.head]['x']
    item.headY = dic[item.head]['y']

    item.addAngle()

    a = limb.delta[-2]
    b = limb.delta[-1]

    R = 15 #Negative threshhold

    if abs(a) > R and abs(0.2*a) > abs(b):
        
        mapNum = map(limb)
        playSound(mapNum)

    return


def map(limb):
    # Determine region of appendage, indexed 1 - 16
    
    mapNum = 0

    x = limb.head.x
    y = limb.head.y
    
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


def playSound(mapNum):

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

    pygame.mixer.init() #Add this line to regular file

    pygame.mixer.music.load(sounds[mapNum])
    pygame.mixer.music.play()




