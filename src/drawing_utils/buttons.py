import cv2
from numpy.typing import NDArray


class Button:
    """Contains static power button location parameters (top left corner and bottom right corner coordinates).

    *(Called by drumGrid class in drumset.py)*"""

    x1 = 0.025
    x2 = 0.25
    y1 = 0.025
    y2 = 0.25


class PowerButton(Button):
    """Creates button denoting current state, which may be hit by user to change."""

    powX = 0.045
    powY = 0.125
    subX = 0.045
    subY = 0.185

    def __init__(self, stateText: str, subText: str, color: tuple, textColor: tuple):

        self.color = color
        self.stateText = stateText
        self.subText = subText
        self.textColor = textColor

    def draw(self, frame: NDArray) -> NDArray:
        """Draws button and text onto the frame image."""

        frameWidth, frameHeight = frame.shape[0:2]

        tL = (int(self.x1 * frameWidth), int(self.y1 * frameHeight))
        bR = (int(self.x2 * frameWidth), int(self.y2 * frameHeight))

        frame = cv2.rectangle(frame, tL, bR, color=self.color, thickness=-1)
        frame = cv2.putText(
            frame,
            self.stateText,
            (int(self.powX * frameWidth), int(self.powY * frameHeight)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=self.textColor,
            thickness=2,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False,
        )
        frame = cv2.putText(
            frame,
            self.subText,
            (int(self.subX * frameWidth), int(self.subY * frameHeight)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=self.textColor,
            thickness=2,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False,
        )

        return frame
