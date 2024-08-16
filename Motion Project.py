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

        locations = np.array(results.pose_landmarks)

        annotated_image = img.copy()

        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), connection_drawing_spec = mp_drawing.DrawingSpec(color = (255,0,255), thickness = 2, circle_radius = 1))

        # Show video at 1 frame per ms
        cv2.imshow("Image", img)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return results.pose_landmarks


# Activate Video / Webcam

cap = cv2.VideoCapture(0)

# mediapipe pose class
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Video pose objectPose
vid_pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)

print(vars(mp_pose.PoseLandmark))

# Pose Landmarks
landmarks = PoseDetection()


print(landmarks)


cap.release()

cv2.destroyAllWindows()




# Store array of locations

# Read hand/foot motions

# Store Appendage location array


## Play associated sounds

