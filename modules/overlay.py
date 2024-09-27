import cv2


class drawClient:
    """Performs drawing operation on current frame."""

    def __init__(self, window):
        
        self.overlays = dict({
            'On': overlay(window.width, window.height, 
                          (0,255,0), "Power: ON", "Hit Here to Switch", (20, 20, 20), (240, 240, 255), bootTextOn = False),
            'Off': overlay(window.width, window.height, 
                           (0, 0, 255), "Power: OFF", "(Hit Here to Switch)", (80, 80, 80), (200, 200, 255), bootTextOn = False),
            'Out': overlay(window.width, window.height, 
                           (50, 90, 0), "Power: OFF", "(Enter Frame to Use)", (60, 60, 60), (150, 150, 150), bootTextOn = True)
        })

    def drawOverlay(self, frame, body, state):
        self.overlays[state].draw(frame, body)


class overlay:
    """Stores overlay content of a given state."""

    def __init__(self, windowWidth, windowHeight, borderColor, btnText, btnSubText, btnColor, btnTextColor, bootTextOn = bool):

        self.width = windowWidth
        self.height = windowHeight
        self.border = border(borderColor)
        self.button = powButton(btnText, btnSubText, btnColor, btnTextColor)
        
        if bootTextOn:
            self.bootText = bootText()
        else:
            self.bootText = None

    def draw(self, frame, body):

        body.landmarks.draw(frame)
        cv2.flip(frame, 1)
        self.button.draw(frame, self.width, self.height)
        self.border.draw(frame, self.width, self.height)

        if self.bootText is not None:
            self.bootText.draw(frame, self.width, self.height)


class powButton:
    
    x1 = 0.025
    x2 = 0.25
    y1 = 0.025
    y2 = 0.25

    powX = 0.045
    powY = 0.125
    subX = 0.045
    subY = 0.185
    
    def __init__(self, stateText, subText, color, textColor):

        self.color = color
        self.stateText = stateText
        self.subText = subText
        self.textColor = textColor

    def draw(self, frame, frameWidth, frameHeight):

        tL = (int(self.x1 * frameWidth), int(self.y1 * frameHeight))
        bR = (int(self.x2 * frameWidth), int(self.y2 * frameHeight))

        frame = cv2.rectangle(frame, tL, bR, color = self.color, thickness = -1)
        frame = cv2.putText(frame, self.stateText, (int(self.powX * frameWidth), int(self.powY * frameHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 2, color = self.textColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)
        frame = cv2.putText(frame, self.subText, (int(self.subX * frameWidth), int(self.subY * frameHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                                fontScale = 1, color = self.textColor, thickness = 2, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

    
class border:
    def __init__(self, color):
        self.color = color

    def draw(self, frame, frameWidth, frameHeight):

        top = int(0.05 * frameWidth)
        bottom = top
        left = int(0.05 * frameHeight)
        right = left

        frame = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, None, self.color)


class bootText:

    # FIXME
    titleX1 = 0.35
    titleY1 = 0.1
    subtitleX1 = 0.4
    subtitleY1 = 0.15

    outBoxX1 = 0.2
    outBoxY1 = 0.85
    outBoxX2 = 0.8
    outBoxY2 = 0.95
    outTextX1 = 0.212
    outTextY1 = 0.925

    def draw(self, frame, frameWidth, frameHeight):

        # Draw "Invisible Drum_Kit" Title
        frame = cv2.putText(frame, "Invisible Drum Kit", (int(0.35 * frameWidth), int(0.1 * frameHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                            fontScale = 4, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)
        frame = cv2.putText(frame, "Inspired by Rowan Atkinson", (int(0.4 * frameWidth), int(0.15 * frameHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                            fontScale = 2, color = (0,0,0), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

        # Draw "Full Body Not in Frame" Message
        tL = (int(0.2 * frameWidth), int(0.85 * frameHeight))
        bR = (int(0.8 * frameWidth), int(0.95 * frameHeight))
        frame = cv2.rectangle(frame, tL, bR, color = (0,0,200), thickness = -1)
        
        frame = cv2.putText(frame, "Full Body Not In Frame", (int(0.212 * frameWidth), int(0.925 * frameHeight)), cv2.FONT_HERSHEY_SIMPLEX, 
                            fontScale = 3, color = (255,255,255), thickness = 6, lineType = cv2.LINE_AA, bottomLeftOrigin = False)

