"""
    Contains tools for defining and operating the invisible drum kit.
"""

import playsound


class drumGrid:
    """
    Grid function
    """

    drumSounds = {
    'Ride': "./Motion-Project/assets/Used_Audio/ride-acoustic02.wav",
    'Tom1': "./Motion-Project/assets/Used_Audio/tom-acoustic01.wav",
    'Tom2': "./Motion-Project/assets/Used_Audio/tom-acoustic02.wav",
    'Hat': "./Motion-Project/assets/Used_Audio/hihat-acoustic01.wav",
    'HatOpen': "./Motion-Project/assets/Used_Audio/hihat-dist02.wav",
    'Crash': "./Motion-Project/assets/Used_Audio/crash-acoustic.wav",
    'FTom': "./Motion-Project/assets/Used_Audio/tom-rototom.wav",
    'SD': "./Motion-Project/assets/Used_Audio/snare-acoustic01.wav",
    'BD': "./Motion-Project/assets/Used_Audio/kick-classic.wav",
    'Special1': './Motion-Project/assets/Used_Audio/clap-808.wav',
    'Special2': './Motion-Project/assets/Used_Audio/cowbell-808.wav',
    'Off': './Motion-Project/assets/Used_Audio/Cowbell.wav',
    'On': './Motion-Project/assets/Used_Audio/Cowbell.wav'
    }

    # Grid layout mapped top to bottom, right to left
    gridLayout = [['Special2', 'Special1'], 
                  ['Ride', 'Tom2', 'Tom1', 'Hat', 'Crash'], 
                  ['FTom', 'SD', 'Hat', 'Crash'], 
                  ['BD', 'Hat']]

    def __init__(self, body, button):
        self.rowRanges = []
        self.colRanges = []
        self.button = button
        self.body = body


class hitClient:
    """
    Collection of functions to determine when drum is hit and output the correct sound.
    """

    # Calibration variables
    visMin = 0.5 # Minimum visibility value for hit

    wLim = 20 # Downward angular velocity activation threshold (for hands)
    vLim = -10 # Downward vertical velocity activation threshold

    minAngle = 20 # Min angle for angle check
    maxAngle = 150 # Max angle for hand angle check
    midMin = 80 # Allow vert check for midrange hand hits
    midMax = 100

    anglSwap = 300 # Min angle change to detect sign change (e.g. + to -)

    hatUpMin = 70

    def __init__(self, body, button):
        self.grid = drumGrid(body, button)

    def hitCheck(self, extremity):
        
        # Prevent false positives from out-of-frame extremities
        if extremity.tail.vis < self.visMin and extremity.head.vis < self.visMin:
            return False

        # Update extremity angles
        extremity.addAngle()

        # Prevent indexError
        if len(extremity.dVert) < 2:
            return False

        # Pull extremity angle behavior for hit check calculations
        a = extremity.angle[-1]
        w1 = extremity.angVel[-2]
        w2 = extremity.angVel[-1]
        v1 = extremity.dVert[-2]
        v2 = extremity.dVert[-1]

        # Detect angle sign change
        if abs(w2) > self.anglSwap:
            extremity.angVel.pop(-1)
            return False

        # Criteria for enabling Vertical Velocity check
        if extremity.type == 'Hand':
            alt = (abs(a) < self.minAngle or abs(a) > self.maxAngle or self.midMin < abs(a) < self.midMax) 
        elif extremity.type == 'Foot':
            alt = True

        # Boolean Checks for hit criteria
        leftHit = self.minAngle < a < self.maxAngle and w1 < -self.wLim and w2 > (0.5 * w1) # Sharp minimum in angular velocity
        rightHit = (-1 * self.maxAngle) < a < (-1 * self.minAngle) and w1 > self.wLim and w2 < (0.5 * w1) # Sharp maximum in angular velocity
        altHit = alt and v1 < self.vLim and v2 > 0.3 * v1 # Sharp minimum in vertical velocity

        return leftHit or rightHit or altHit
    
    def playHit(self, extremity):
    
        # Get drum mapping
        mapVal = self.getMapVal(extremity)
        
        # Check for false positive from out-of-frame extremity
        if mapVal == False:
            pass

        # Open Hi Hat when left foot angled upwards
        elif mapVal == 'Hat' and self.body.extremities[2].head.vis > 0.5 and abs(self.body.extremities[2].angle[-1]) > self.hatUpMin:
            mapVal = 'HatOpen'

        # Button trigger
        elif mapVal == 'Button':
            if appState.activeSound == True:
                appState.activeSound = False
                playsound(self.grid.drumSounds['Off'], block = False)
                pass
            else:
                appState.activeSound = True
                mapVal = 'On'

        # Play mapped Audio when sound setting on
        if appState.activeSound == True:
            playsound(sounds[mapVal], block = False)

    def getMapVal(self, extremity):
        """Determine map location of limb for sound output
        
        Keyword arguments:
        extremity -- 
        """

        x = extremity.head.x
        y = extremity.head.y

        # Prevent leakage of out-of-frame hit triggers
        if not (0 <= x <= 1 and 0 <= y <= 1):
            return False

        # Auto-map feet
        if extremity.type == 'Foot' and extremity.side == 'Left':
            return 'Hat'
        elif extremity.type == 'Foot' and extremity.side == 'Right':
            return 'BD'

        rowMap = int
        colMap = int

        # Check for button hit assuming image flipped horizontally
        if (1 - self.button.x1) > x > (1 - self.button.x2) and self.button.y1 < y < self.button.y2:
            return 'Button'

        # Map Row, then Column of extremity head
        for i in range(len(self.rowRanges) - 1):
            if self.rowRanges[i] <= y <= self.rowRanges[i + 1]:
                rowMap = i

        for j in range(len(self.colRanges[rowMap]) - 1):
            if self.colRanges[rowMap][j] <= x <= self.colRanges[rowMap][j + 1]:
                colMap = j
            
        # Convert grid location to drum code
        mapVal = self.gridLayout[rowMap][colMap]

        return mapVal


    def updateGrid(self, torso):
        """
        Calculate hit grid from torso points
        """

        # Reinitialize torso points
        leftShoulder = torso[0]
        rightShoulder = torso[1]
        leftHip = torso[2]
        rightHip = torso[3]

        # Vertical references
        waistY = avg(leftHip.y, rightHip.y)
        shoulderY = avg(leftShoulder.y, rightShoulder.y)
        torsoSplitY = (1/3) * (waistY - shoulderY)

        # Horizontal references
        waistDisp = leftHip.x - rightHip.x
        torsoSplitX = avg(leftHip.x, rightHip.x)

        # Calculate rows endpoints, from Top to Bottom
        self.rowRanges = [0, shoulderY - torsoSplitY, waistY - torsoSplitY, waistY + torsoSplitY, 1]
        
        # Calculate sub-column endpoints by Row, Top to Bottom and Right to Left (due to image flip)
        self.colRanges = [[0, torsoSplitX, 1], 
                    [0, rightShoulder.x - waistDisp, rightShoulder.x, torsoSplitX, leftShoulder.x + waistDisp, 1], 
                    [0, rightShoulder.x, leftShoulder.x, leftShoulder.x + waistDisp, 1], 
                    [0, torsoSplitX, 1]]
   

def avg(x, y):
# Calculate average of two points

    average = (x + y) / 2
    return average
