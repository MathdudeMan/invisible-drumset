"""
    Contains tools for defining and operating the invisible drum kit.
"""

from .overlay import button

from playsound import playsound
import pygame.mixer as pg
# import sounddevice as sd
# import soundfile as sf


class drumsetClient:
    """Performs functions for playing an invisible on-screen drum kit."""

    stateConversion = {True: 'On', False: 'Off'}

    def __init__(self, body):

        self.body = body
        self.grid = drumGrid(self.body)
        self.hitClient = hitClient()
        self.activeSound = False

    def playDrum(self, imgMirror):
        """Returns state indicator: 'On' if sound is active, 'Off' otherwise."""
        
        self.grid.update()

        for ext in self.body.extremities:

            isHit = self.hitClient.hitCheck(ext)
            if isHit is False:
                continue

            mapVal = self.grid.getMapVal(ext, imgMirror)
            if mapVal == None:
                continue
            elif mapVal == 'Button':
                self.triggerButton()
            elif self.activeSound:
                self.triggerAudio(mapVal)

        return self.stateConversion[self.activeSound]

    def triggerButton(self):

        self.activeSound = not self.activeSound
        self.triggerAudio(self.stateConversion[self.activeSound])

    def triggerAudio(self, mapVal):
    
        playsound(self.grid.drumSounds[mapVal], block = False)


class hitClient:
    """
    Collection of functions for calculating drum hit occurrences and outputting sounds.
    """

    # Minimum visibility value for hitCheck
    visMin = 0.5

    # Angular / vertical velocity activation thresholds
    wLim = 20
    vLim = -10

    # Spike ratios
    wRatio = 0.5
    vRatio = 0.3

    minAngle = 20 # Hand angle hit threshold
    maxAngle = 150
    midMin = 80 # Midrange hit threshold
    midMax = 100
    anglSwap = 300 # Min angle change to detect sign change (e.g. + to -)


    def hitCheck(self, extremity):

        # Bypass out-of-frame extremity
        if extremity.tail.vis < self.visMin and extremity.head.vis < self.visMin:
            return False

        # Pull extremity angle behavior for hit check calculations
        try:
            a = extremity.angle[-1]
            w1 = extremity.angVel[-2]
            w2 = extremity.angVel[-1]
            v1 = extremity.dVert[-2]
            v2 = extremity.dVert[-1]
        except IndexError:
            return False

        # Bypass for angle sign change
        if abs(w2) > self.anglSwap:
            extremity.angVel.pop(-1)
            return False
        
        # Criteria for enabling Vertical Velocity check
        if extremity.type == 'Hand':
            alt = (abs(a) < self.minAngle or abs(a) > self.maxAngle or self.midMin < abs(a) < self.midMax) 
        elif extremity.type == 'Foot':
            alt = True

        # Check for sharp min in absolute angular velocity / vertical velocity
        leftHit = self.minAngle < a < self.maxAngle and w1 < -self.wLim and w2 > (self.wRatio * w1)
        rightHit = self.minAngle < (-a) < self.maxAngle and w1 > self.wLim and w2 < (self.wRatio * w1)
        altHit = alt and v1 < self.vLim and v2 > (self.vRatio * v1) 

        return leftHit or rightHit or altHit


class drumGrid:
    """
    Contains basic parameters for drum kit grid boxes. Gridlines are defined in the x and y directions.
    """

    hatOpenAngle = 70 # Minimum left foot angle to activate an open hat sound

    # Grid layout mapped top to bottom, right to left (from mediapipe perspective)
    gridLayout = [['Special2', 'Special1'], 
                  ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], 
                  ['FTom', 'SD', 'Hat', 'Crash'], 
                  ['BD', 'Hat']]

    drumSounds = {
    'Ride': "./invisible-drumset/assets/Used_Audio/ride-acoustic02.wav",
    'Tom1': "./invisible-drumset/assets/Used_Audio/tom-acoustic01.wav",
    'Tom2': "./invisible-drumset/assets/Used_Audio/tom-acoustic02.wav",
    'Hat': "./invisible-drumset/assets/Used_Audio/hihat-acoustic01.wav",
    'HatOpen': "./invisible-drumset/assets/Used_Audio/hihat-dist02.wav",
    'Crash': "./invisible-drumset/assets/Used_Audio/crash-acoustic.wav",
    'FTom': "./invisible-drumset/assets/Used_Audio/tom-rototom.wav",
    'SD': "./invisible-drumset/assets/Used_Audio/snare-acoustic01.wav",
    'BD': "./invisible-drumset/assets/Used_Audio/kick-classic.wav",
    'Special1': './invisible-drumset/assets/Used_Audio/clap-808.wav',
    'Special2': './invisible-drumset/assets/Used_Audio/cowbell-808.wav',
    'Off': './invisible-drumset/assets/Used_Audio/Cowbell.wav',
    'On': './invisible-drumset/assets/Used_Audio/Cowbell.wav'
    }

    def __init__(self, body):
        
        self.body = body
        self.rowGridlines = [] * (len(self.gridLayout) + 1)
        self.colGridlines = [] * (len(self.gridLayout))

        self.endX = body.maxX
        self.endY = body.maxY

        self.powButton = button()
        self.powButton.x1 *= self.endX
        self.powButton.x2 *= self.endX
        self.powButton.y1 *= self.endY
        self.powButton.y2 *= self.endY

    def update(self):
        """
        Uses body torso to update gridline locations.
        """

        # Extract torso points
        leftShoulder = self.body.torso[0]
        rightShoulder = self.body.torso[1]
        leftHip = self.body.torso[2]
        rightHip = self.body.torso[3]

        # Calculate vertical references
        shoulderY = avg(leftShoulder.y, rightShoulder.y)
        waistY = avg(leftHip.y, rightHip.y)
        torsoHeight = waistY - shoulderY
        torsoDiv = (1/3) * torsoHeight

        # Calculate horizontal references
        waistLength = leftHip.x - rightHip.x
        torsoSplitX = avg(leftHip.x, rightHip.x)

        # Calculate row gridlines, from Top to Bottom
        self.rowGridlines = [0, shoulderY - torsoDiv, waistY - torsoDiv, waistY + torsoDiv, self.endY]
        
        # Calculate sub-column gridlines by Row, Top to Bottom and Right to Left (due to image flip)
        self.colGridlines = [[0, torsoSplitX, self.endX], 
                    [0, rightShoulder.x - waistLength, rightShoulder.x, torsoSplitX, leftShoulder.x + waistLength, self.endX], 
                    [0, rightShoulder.x, leftShoulder.x, leftShoulder.x + waistLength, self.endX], 
                    [0, torsoSplitX, self.endX]]

    def getMapVal(self, extremity, imgMirror):
        """Determine map location of limb for sound output."""

        x = extremity.head.x
        y = extremity.head.y
        rowMap = 0
        colMap = 0

        if not (0 < x < self.endX and 0 < y < self.endY):
            return None

        # Auto-map feet
        if extremity.type == 'Foot' and extremity.side == 'Left':
            return 'Hat'
        elif extremity.type == 'Foot' and extremity.side == 'Right':
            return 'BD'

        # Check for button hit
        buttonCheckX = False
        if imgMirror:
            buttonCheckX = (self.endX - self.powButton.x1) > x > (self.endX - self.powButton.x2) 
        else:
            buttonCheckX = self.powButton.x1 < x < self.powButton.x2

        if buttonCheckX and self.powButton.y1 < y < self.powButton.y2:
            return 'Button'

        # Map Row and Column of extremity head
        for i in range(len(self.rowGridlines) - 1):
            if self.rowGridlines[i] <= y <= self.rowGridlines[i + 1]:
                rowMap = i
                break

        for j in range(len(self.colGridlines[rowMap]) - 1):
            if self.colGridlines[rowMap][j] <= x <= self.colGridlines[rowMap][j + 1]:
                colMap = j
                break
            
        mapVal = self.gridLayout[rowMap][colMap]

        # Open Hi Hat when left foot angled upwards
        if mapVal == 'Hat' and self.body.extremities[2].head.vis > 0.5 and abs(self.body.extremities[2].angle[-1]) > self.hatOpenAngle:
            mapVal = 'HatOpen'

        return mapVal
        

def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average
