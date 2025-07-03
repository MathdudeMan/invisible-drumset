from modules.frame_io import FrameManager
from modules.body import Body
from modules.drawing import DrawingClient
from modules.drumset import DrumsetClient

class App:

    def __init__(self):

        self.enabled = True
        self.state = 'Off'

        self.frame_manager = FrameManager()
        self.window = self.frame_manager.window

        self.body = Body(self.window)
        self.drawing_client = DrawingClient(self.window)
        self.drumset = DrumsetClient(self.body)

        self.current_frame = None
        self.image_mirrored = True

    def run(self):
        """Run main app loop."""
        
        while self.enabled == True:
        
            # Get frame
            self.current_frame = self.frame_manager.getFramePackage()
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
            self.enabled = self.frame_manager.display(self.current_frame.imgOutput)

def main():

    newApp = App()
    newApp.run()


if __name__ == "__main__":
    main()