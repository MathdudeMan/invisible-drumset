"""Contains tools for defining and operating the invisible drum kit."""

from .drawing import button
import os
from playsound import playsound

# Alternative sound playback libraries
# import pygame.mixer as pg
# import sounddevice as sd
# import soundfile as sf


class drumsetClient:
    """Contains functions for playing the invisible on-screen drum kit."""

    state_dict = {True: 'On', False: 'Off'}

    def __init__(self, body):

        self.body = body
        self.grid = drumGrid(self.body)
        self.hitClient = hitClient()
        self.sound_active = False

    def playDrum(self, imgMirror) -> bool:
        """Returns state indicator: 'On' if sound is active, 'Off' otherwise."""
        
        self.grid.update_gridlines()

        for ext in self.body.extremities:

            isHit = self.hitClient.check_hit(ext)
            if isHit is False:
                continue

            mapVal = self.grid.get_location_id(ext, imgMirror)
            if mapVal == None:
                continue
            elif mapVal == 'Button':
                self._triggerButton()
            elif self.sound_active:
                self._triggerAudio(mapVal)

        return self.state_dict[self.sound_active]

    def _triggerButton(self):

        self.sound_active = not self.sound_active
        self._triggerAudio(self.state_dict[self.sound_active])

    def _triggerAudio(self, mapVal: str):
    
        playsound(self.grid.drum_sound_paths[mapVal], block = False)


class hitClient:
    """Holds function for calculating drum hit occurrences and outputting sounds."""

    # Minimum visibility value for hitCheck
    visMin = 0.5

    # Angular / vertical velocity activation thresholds
    wLim = 20
    vLim = -10

    # Value drop ratio triggers
    wRatio = 0.4
    vRatio = 0.3

    minAngle = 20 # Hand angle hit threshold
    maxAngle = 150
    midMin = 80 # Midrange hit threshold
    midMax = 100
    angleSwap = 300 # Min angle change to detect sign change (e.g. + to -)


    def check_hit(self, extremity) -> bool:
        """Checks extremity for hit based on change in changes in angle or vertical components.
        Seeks for sharp spike in change (velocity) values."""

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
        if abs(w2) > self.angleSwap:
            extremity.angVel.pop(-1)
            return False

        vert_check = False
        # Criteria for enabling Vertical Velocity check
        if extremity.type == 'Hand':
            vert_check = (abs(a) < self.minAngle or abs(a) > self.maxAngle or self.midMin < abs(a) < self.midMax) 
        elif extremity.type == 'Foot':
            vert_check = True

        # Check for sharp min in absolute angular velocity / vertical velocity
        leftHit = self.minAngle < a < self.maxAngle and w1 < -self.wLim and w2 > (self.wRatio * w1)
        rightHit = self.minAngle < (-a) < self.maxAngle and w1 > self.wLim and w2 < (self.wRatio * w1)
        vert_hit = vert_check and v1 < self.vLim and v2 > (self.vRatio * v1) 

        return leftHit or rightHit or vert_hit



class drumGrid:
    """Contains basic parameters for drum kit grid boxes. Gridlines are defined in the x and y directions."""

    open_hat_angle = 70 # Minimum left foot angle to activate an open hat sound

    # Grid layout mapped top to bottom, right hand side to left hand side
    grid_layout = [['Special2', 'Special1'], 
                  ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], 
                  ['FTom', 'SD', 'Hat', 'Crash'], 
                  ['BD', 'Hat']]

    assets_dir = os.path.join(os.path.pardir, 'assets', 'Used_Audio')
    drum_sound_paths = {
        'Ride': os.path.join(assets_dir, "ride-acoustic02.wav"),
        'Tom1': os.path.join(assets_dir, "tom-acoustic01.wav"),
        'Tom2': os.path.join(assets_dir, "tom-acoustic02.wav"),
        'Hat': os.path.join(assets_dir, "hihat-acoustic01.wav"),
        'HatOpen': os.path.join(assets_dir, "hihat-dist02.wav"),
        'Crash': os.path.join(assets_dir, "crash-acoustic.wav"),
        'FTom': os.path.join(assets_dir, "tom-rototom.wav"),
        'SD': os.path.join(assets_dir, "snare-acoustic01.wav"),
        'BD': os.path.join(assets_dir, "kick-classic.wav"),
        'Special1': os.path.join(assets_dir, "clap-808.wav"),
        'Special2': os.path.join(assets_dir, "cowbell-808.wav"),
        'Off': os.path.join(assets_dir, "Cowbell.wav"),
        'On': os.path.join(assets_dir, "Cowbell.wav")
    }

    def __init__(self, body):
        
        self.body = body
        self.horizontal_gridlines = [] * (len(self.grid_layout) + 1)
        self.vertical_gridlines = [] * (len(self.grid_layout))

        self.endX = body.maxX
        self.endY = body.maxY

        self.powButton = button()
        self.powButton.x1 *= self.endX
        self.powButton.x2 *= self.endX
        self.powButton.y1 *= self.endY
        self.powButton.y2 *= self.endY

    def update_gridlines(self):
        """Uses body torso to update gridline locations."""

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

        # Calculate horizontal gridlines, from Top to Bottom
        self.horizontal_gridlines = [0, shoulderY - torsoDiv, waistY - torsoDiv, waistY + torsoDiv, self.endY]
        
        # Calculate vertical gridlines within each row, Top to Bottom and Right to Left (based on gridLayout)
        self.vertical_gridlines = [[0, torsoSplitX, self.endX], 
                    [0, rightShoulder.x - waistLength, rightShoulder.x, leftHip.x, leftShoulder.x + waistLength, self.endX], 
                    [0, rightShoulder.x, leftShoulder.x, leftShoulder.x + waistLength, self.endX], 
                    [0, torsoSplitX, self.endX]]

    def get_location_id(self, extremity, imgMirror) -> str:
        """Determines present map id of limb. Returns the associated string identifier, adjusted by defined parameters."""

        x = extremity.head.x
        y = extremity.head.y

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

        mapVal = self._map_to_grid(x,y)

        # Open Hi Hat when left foot angled upwards
        if mapVal == 'Hat' and self.body.extremities[2].head.vis > 0.5 and abs(self.body.extremities[2].angle[-1]) > self.open_hat_angle:
            mapVal = 'HatOpen'

        return mapVal
        
    def _map_to_grid(self, xLoc: float, yLoc: float) -> str:
        """Maps row and column of extremity head and returns the associated string identifier."""

        rowMap = 0
        colMap = 0

        for i in range(len(self.horizontal_gridlines) - 1):
            if self.horizontal_gridlines[i] <= yLoc <= self.horizontal_gridlines[i + 1]:
                rowMap = i
                break

        for j in range(len(self.vertical_gridlines[rowMap]) - 1):
            if self.vertical_gridlines[rowMap][j] <= xLoc <= self.vertical_gridlines[rowMap][j + 1]:
                colMap = j
                break

        print("x: " + str(xLoc) + ", y: " + str(yLoc))
        print("Row: " + str(rowMap) + ", Col: " + str(colMap))
        print(self.grid_layout[rowMap][colMap])

        return self.grid_layout[rowMap][colMap]
    


def avg(x: float | int, y: float | int) -> float:
    """Calculate average of two points"""

    average = (x + y) / 2
    return average
