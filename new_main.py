from modules.frameWindow import frameManager
from modules.body import body
from modules.overlay import drawClient
from modules.drumset import hitClient

class app:
    """App definition"""
    def __init__(self):

        self.enabled = True

        self.fm = frameManager()
        self.dc = drawClient(self.fm.window)
        # self.hc = hitClient()

        self.state = 'Off'
        self.body = body()
        self.framePack = None

        self.outputFrame = None
        self.dataFrame = None


    def main(self):
        
        while self.enabled == True:
        
            self.framePack = self.fm.getFramePackage()
            self.body.update(self.framePack.imgReadable)

            if self.body.inFrame is False:
                self.state = 'Out'
            # else:
                # self.state = drumsetClient.hitCheck(self.body, self.state)

            self.dc.drawOverlay(self.framePack.imgOutput, self.body, self.state)

            self.enabled = self.fm.display(self.framePack.imgOutput)

def main():

    newApp = app()
    newApp.main()

if __name__ == "__main__":
    main()