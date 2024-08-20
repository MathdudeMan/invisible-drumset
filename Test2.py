import cv2
import mediapipe as mp
import math

class limb:
    def __init__(self, tail, head):
        self.tail = tail
        self.head = head
        self.angle = [] #Vector angle values
        self.delta = [] #Angular velocity values

    def addAngle(self):
        
        deltaX = self.head.x - self.tail.x
        deltaY = self.head.y - self.tail.y
        theta = math.atan2(deltaX, deltaY)

        self.angle.append(theta)

        if self.delta.length > 1:
            change = self.angle[-1] - self.angle[-2]
            self.delta.append(change)


# Init mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Init video pose object
vid_pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Activate Video / Webcam
cap = cv2.VideoCapture(0)


success, img = cap.read()

img = cv2.resize(img, (800, 600))
imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
results = vid_pose.process(imgRGB)

# Read & draw all landmarks
landmarks = results.pose_landmarks

print(landmarks)
print(type(landmarks))



# Setup pose landmarks
markPairs = [(15,19),(16,20),(29,31),(30,32)]
limbs = ["leftHand", "rightHand", "leftFoot", "rightFoot"]

limbs = []

leftHand = limb(15,19)
rightHand = limb(16,20)
leftFoot = limb(29,31)
rightFoot = limb(30,32)

limbs.append(leftHand)


goodMarks = [15,19,16,20,29,31,30,32]
markNames = ()
for num in goodMarks:
    markNames += (mp_pose.PoseLandmark(num), )


# Get hand / foot landmarks
dic = {}
# for mark, data_point in zip(mp_pose.PoseLandmark, 
                            
points = []
for data_point in landmarks.landmark:
  keypoints.append({
    'X': data_point.x,
    'Y': data_point.y,
    'Z': data_point.z,
    'Visibility': data_point.visibility,
    })
    
