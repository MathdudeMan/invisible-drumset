from modules.frameManager import frameManager
from modules.body import body
from modules.overlay import drawClient
from modules.drumset import drumsetClient

class app:

    def __init__(self):

        self.enabled = True

        self.frm = frameManager()
        self.win = self.frm.window

        self.dwg = drawClient(self.win)
        self.bod = body(self.win)
        self.kit = drumsetClient(self.bod)

        self.framePack = None
        self.state = 'Off'
        self.imgMirror = True

    def main(self):
        
        while self.enabled == True:
        
            self.framePack = self.frm.getFramePackage()
            self.bod.update(self.framePack.imgReadable)

            if self.bod.inFrame:
                self.state = self.kit.playDrum(self.imgMirror)
            else:
                self.state = 'Out'

            self.framePack.imgOutput = self.dwg.drawOverlay(self.framePack.imgOutput, 
                                                           self.bod, self.state, self.imgMirror)
            self.enabled = self.frm.display(self.framePack.imgOutput)


def main():

    newApp = app()
    newApp.main()

if __name__ == "__main__":
    main()