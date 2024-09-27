"""
Includes tools for constructing the program's user interface.
"""

import tkinter as tk
import cv2


class frameManager:
    """Performs operations involving camera frame retrieval and display"""

    def __init__(self):

        self.window = window("Motion Cap")
        self.cam = camera(0)
        self.window.assignSize(self.cam)

        self.framePack = framePackage()

    def getFramePackage(self):
        newFrame = self.cam.read()
        self.framePack.packImage(newFrame, self.window.width, self.window.height)
        return self.framePack
        
    def display(self, frame):
        """Returns True if window remains open after frame, False if closed."""
    
        cv2.imshow(self.window.title, frame)

        # Frame buffer (Conditional is always False)
        if cv2.waitKey(2) == -2:
            pass

        # If window closed, end program activity
        if cv2.getWindowProperty(self.window.title, cv2.WND_PROP_VISIBLE) < 1:
            self.cam.close
            return False
        
        return True
    

class framePackage:
    """Stores two copies of image, one for pose estimation and the other for user output."""

    def __init__(self):

        self.imgOutput = None
        self.imgReadable = None

    def packImage(self, rawImage, windowWidth, windowHeight):

        self.imgOutput = cv2.resize(rawImage, (windowWidth, windowHeight))
        self.imgReadable = cv2.cvtColor(self.imgOutput, cv2.COLOR_BGR2RGB)

class window:
    """Creates window object to hold camera output."""

    def __init__(self, title):

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
    def __init__(self, port):
        self.cap = cv2.VideoCapture(port)
        self.width = int(self.cap.get(3)) #640
        self.height = int(self.cap.get(4)) #480

    def read(self):
        isValid, img = self.cap.read() 
        if isValid:
            return img
        else:
            return False

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows
