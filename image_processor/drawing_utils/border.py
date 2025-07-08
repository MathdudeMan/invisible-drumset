import cv2
from numpy.typing import NDArray


class Border:
    """Creates solid-color border around given frame."""

    borderThickness = 0.05

    def __init__(self, color: tuple):
        self.color = color

    def draw(self, frame: NDArray) -> NDArray:
        """Returns edited image with border around it."""

        frameWidth, frameHeight = frame.shape[0:2]

        top = int(self.borderThickness * frameHeight)
        bottom = top
        left = int(self.borderThickness * frameWidth)
        right = left

        frame = cv2.copyMakeBorder(
            frame,
            top,
            bottom,
            left,
            right,
            borderType=cv2.BORDER_CONSTANT,
            dst=None,
            value=self.color,
        )
        return frame


class TitleText:
    """Creates title and startup text on given frame."""

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

    def draw(self, frame) -> NDArray:
        """Draws title and startup message content onto frame image."""

        frameWidth, frameHeight = frame.shape[0:2]

        # "Invisible Drum_Kit" Title
        frame = cv2.putText(
            frame,
            "Invisible Drum Kit",
            (int(self.titleX1 * frameWidth), int(self.titleY1 * frameHeight)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 0),
            thickness=6,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False,
        )
        frame = cv2.putText(
            frame,
            "Inspired by Rowan Atkinson",
            (int(self.subtitleX1 * frameWidth), int(self.subtitleY1 * frameHeight)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 0),
            thickness=6,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False,
        )

        # "Full Body Not in Frame" Message
        tL = (int(self.outBoxX1 * frameWidth), int(self.outBoxY1 * frameHeight))
        bR = (int(self.outBoxX2 * frameWidth), int(self.outBoxY2 * frameHeight))
        frame = cv2.rectangle(frame, tL, bR, color=(0, 0, 200), thickness=-1)

        frame = cv2.putText(
            frame,
            "Full Body Not In Frame",
            (int(self.outTextX1 * frameWidth), int(self.outTextY1 * frameHeight)),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=6,
            lineType=cv2.LINE_AA,
            bottomLeftOrigin=False,
        )

        return frame
