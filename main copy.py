from modules_copy.frame_io import frameManager
from modules_copy.body import body
from modules_copy.drawing import drawClient
from modules_copy.drumset import drumsetClient


class app:

    def __init__(self):

        self.enabled = True
        self.state = 'Off'

        self.frame_manager = frameManager()
        self.window = self.frame_manager.window

        self.body = body(self.window)
        self.draw_client = drawClient(self.window)
        self.drumset = drumsetClient(self.body)

        self.current_frame = None
        self.image_mirrored = True

    def run(self):
        """Run main app loop."""
        
        while self.enabled:
        
            self.current_frame = self.frame_manager.getFramePackage()
            self.body.update(self.current_frame.imgReadable)

            if self.body.isInFrame:
                self.state = self.drumset.playDrum(self.image_mirrored)
            else:
                self.drumset.sound_active = False
                self.state = 'Out'

            self.current_frame.imgOutput = self.draw_client.drawOverlay(self.current_frame.imgOutput, 
                                                           self.body, self.state, self.image_mirrored)
            self.enabled = self.frame_manager.display(self.current_frame.imgOutput)

class app_edit:

    def __init__(self):

        self.enabled = True
        self.state = 'Off'

        self.frame_manager = frameManager()
        self.window = self.frame_manager.window

        self.body = body(self.window)
        self.draw_client = drawClient(self.window)
        self.drumset = drumsetClient(self.body)

        self.current_frame = None
        self.image_mirrored = True

    def run(self):
        """Run main app loop."""
        
        while self.enabled:
        
            self.current_frame = self.frame_manager.getFramePackage()
            self.body.update(self.current_frame.imgReadable)

            if self.body.isInFrame:
                self.state = self.drumset.playDrum(self.image_mirrored)
            else:
                self.drumset.sound_active = False
                self.state = 'Out'

            self.current_frame.imgOutput = self.draw_client.drawOverlay(self.current_frame.imgOutput, 
                                                           self.body, self.state, self.image_mirrored)
            self.enabled = self.frame_manager.display(self.current_frame.imgOutput)



def main():

    newApp = app()
    newApp.run()


if __name__ == "__main__":
    main()