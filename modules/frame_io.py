"""Includes tools for producing and storing video frames with OpenCV, 
    including camera and program window objects."""

import tkinter as tk
import cv2

tk.Tk().withdraw()

class FrameManager:
    """Performs operations involving video frame retrieval and display.
    
    User webcam (port 0) set as camera by default."""

    def __init__(self):

        cam_port = 0
        self.cam = camera(cam_port)

        self.window = window("Motion Cap")
        self.window.assignSize(self.cam)

        self.framePack = framePackage()

    def getFramePackage(self) -> 'framePackage':
        """Retrieves current video frame and returns frame package."""

        newFrame = self.cam.read()
        self.framePack.packImage(newFrame, self.window.width, self.window.height)
        return self.framePack
        
    def display(self, frame) -> bool:
        """Returns True if window remains open after frame, False if closed."""
    
        cv2.imshow(self.window.title, frame)

        # Frame buffer (Conditional is always False)
        if cv2.waitKey(2) == -2:
            pass

        # If window closed, end program activity. Responsible for ending program.
        if cv2.getWindowProperty(self.window.title, cv2.WND_PROP_VISIBLE) < 1:
            self.cam.close
            return False
        
        return True
    

class framePackage:
    """Stores two copies of image, one formatted for pose estimation and the other for window display."""

    def __init__(self):

        self.imgOutput = None
        self.imgReadable = None

    def packImage(self, rawImage, windowWidth: int, windowHeight: int):
        """Resizes given frame to window size and creates duplicate formatted to RGB for mediapipe analysis."""

        self.imgOutput = cv2.resize(rawImage, (windowWidth, windowHeight))
        self.imgReadable = cv2.cvtColor(self.imgOutput, cv2.COLOR_BGR2RGB)


class window:
    """Window object for holding user-facing content."""

    def __init__(self, title: str):

        self.title = title
        cv2.namedWindow(self.title, cv2.WINDOW_GUI_NORMAL)

        self.width = None
        self.height = None

    def assignSize(self, cam):
        """Scale window so both height and width span the screen."""

        root = tk.Tk()
        screenWidth, screenHeight = int(root.winfo_screenwidth()), int(root.winfo_screenheight())

        scale = max((screenWidth / cam.width), (screenHeight / cam.height))
        self.width = int(cam.width * scale)
        self.height = int(cam.height * scale)
        cv2.resizeWindow(self.title, self.width, self.height)

        
class camera:
    """Holds data for camera used."""

    def __init__(self, port: int):

        self.cap = cv2.VideoCapture(port)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))

    def read(self) -> type | bool:

        isValid, img = self.cap.read() 
        if isValid:
            return img
        else:
            return False

    def close(self):

        self.cap.release()
        cv2.destroyAllWindows
