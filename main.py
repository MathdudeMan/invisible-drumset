from modules.frame_io import FrameManager, window, camera, framePackage
from modules.body import Body
from modules.drawing import DrawingClient
from modules.drumset import DrumsetClient

import cv2

CAMERA_PORT = 0


class App:

    def __init__(self):

        self.cam = camera(CAMERA_PORT)
        self.window = window("Motion Cap")
        self.window.assignSize(self.cam)

        self.enabled = True
        self.state = 'Off'

        # self.frame_manager = FrameManager()
        # self.window = self.frame_manager.window

        self.body = Body(self.window)
        self.drawing_client = DrawingClient(self.window)
        self.drumset = DrumsetClient(self.body)

        self.current_frame = None
        self.image_mirrored = True

    def getFramePackage(self) -> framePackage:
        """Retrieves current video frame and returns frame package."""

        newFrame = self.cam.read()
        framePack = framePackage()
        framePack.packImage(newFrame, self.window.width, self.window.height)
        return framePack
    
    def display_frame(self, frame) -> bool:
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

    def run(self):
        """Run main app loop."""
        
        while self.enabled == True:
        
            # Get frame
            self.current_frame = self.getFramePackage()
            self.body.update(self.current_frame.imgReadable)

            if self.body.isInFrame:
                self.state = self.drumset.playDrum(self.image_mirrored)
            else:
                self.drumset.sound_active = False
                self.state = 'Out'

            # Draw on frame
            self.current_frame.imgOutput = self.drawing_client.drawOverlay(self.current_frame.imgOutput,            
                                                           self.state, self.image_mirrored)
            self.body.landmarks.draw(self.current_frame.imgOutput)

            # Display frame
            self.enabled = self.display_frame(self.current_frame.imgOutput)


def main():

    newApp = App()
    newApp.run()


if __name__ == "__main__":
    main()