import cv2
import numpy as np
import mediapipe as mp
import numpy as np
import pygame


def PoseDetection():

    while True:

        success, img = cap.read()
        if not success:
            break

        img = cv2.resize(img, (800, 600))

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = vid_pose.process(imgRGB)

        landmarks = results.pose_landmarks

        annotated_image = img.copy()

        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), connection_drawing_spec = mp_drawing.DrawingSpec(color = (255,0,255), thickness = 2, circle_radius = 1))

        # Show video at 1 frame per ms
        cv2.imshow("Image", img)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return landmarks


# Activate Video / Webcam

cap = cv2.VideoCapture(0)

# mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Video pose objectPose
vid_pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)


# Pose Landmarks
landmarks = PoseDetection()

goodMarks = (0,15,16,19,20,29,30,31,32)

# Get pose landmarks and all detected points
dic = {}
for mark, data_point in zip(goodMarks, landmarks.landmark):
    dic[mark.value] = dict(landmark = mark.name, 
        x = data_point.x,
        y = data_point.y,
        z = data_point.z,
        vis = data_point.visibility)

# hand = dic[19]['vis']
# print(hand)

ranges = [[0,0.3,0.5,0.7,1], [0,0.25,0.5,0.75,1]]


cap.release()

cv2.destroyAllWindows()



# Read hand/foot motions

## Play associated sounds

