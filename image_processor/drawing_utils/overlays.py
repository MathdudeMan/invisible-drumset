"""Contains tools for drawing a frontend overlay on a given video frame with OpenCV."""

from numpy.typing import NDArray

from .buttons import PowerButton
from .border import Border, TitleText

from ..utils import State


class DrawingClient:
    """Performs drawing operations on current frame."""

    def __init__(self):

        self.overlays = dict(
            {
                State.ON: Overlay(
                    (0, 255, 0),
                    "Power: ON",
                    "Hit Here to Switch",
                    (20, 20, 20),
                    (240, 240, 255),
                    titleTextActive=False,
                ),
                State.OFF: Overlay(
                    (0, 0, 255),
                    "Power: OFF",
                    "(Hit Here to Switch)",
                    (80, 80, 80),
                    (200, 200, 255),
                    titleTextActive=False,
                ),
                State.OUT: Overlay(
                    (50, 90, 0),
                    "Power: OFF",
                    "(Enter Frame to Use)",
                    (60, 60, 60),
                    (150, 150, 150),
                    titleTextActive=True,
                ),
            }
        )

    def draw_overlay(self, frame: NDArray, state: State) -> NDArray:
        """Draw overlay given current program state."""

        frame = self.overlays[state].draw(frame)
        return frame


# TODO Finish default overlays
class Overlay:
    """Stores overlay content of a given state, including border, button, and title text."""

    def __init__(
        self,
        borderColor: tuple,
        btnText: str,
        btnSubText: str,
        btnColor: tuple,
        btnTextColor: tuple,
        titleTextActive: bool,
    ):

        self.border = Border(borderColor)
        self.button = PowerButton(btnText, btnSubText, btnColor, btnTextColor)

        if titleTextActive:
            self.titleText = TitleText()
        else:
            self.titleText = None

    def draw(self, frame: NDArray) -> NDArray:
        """
        Draw button, title text, and border onto a frame. Flips frame if image Mirror active.
        Returns edited frame.
        """

        frame = self.button.draw(frame)

        if self.titleText is not None:
            frame = self.titleText.draw(frame)

        frame = self.border.draw(frame)
        return frame


# TODO
class OnOverlay(Overlay):
    def __init__(
        self,
        borderColor: tuple = (0, 255, 0),
        btnText: str = "Power: ON",
        btnSubText: str = "Hit Here to Switch",
        btnColor: tuple = (20, 20, 20),
        btnTextColor: tuple = (240, 240, 255),
        titleTextActive: bool = False,
    ):

        self.border = Border(borderColor)
        self.button = PowerButton(btnText, btnSubText, btnColor, btnTextColor)

        if titleTextActive:
            self.titleText = TitleText()
        else:
            self.titleText = None


# TODO
class OffOverlay(Overlay):
    def __init__(
        self,
        borderColor: tuple = (0, 255, 0),
        btnText: str = "Power: ON",
        btnSubText: str = "Hit Here to Switch",
        btnColor: tuple = (20, 20, 20),
        btnTextColor: tuple = (240, 240, 255),
        titleTextActive: bool = False,
    ):

        self.border = Border(borderColor)
        self.button = PowerButton(btnText, btnSubText, btnColor, btnTextColor)

        if titleTextActive:
            self.titleText = TitleText()
        else:
            self.titleText = None


class OutOverlay(Overlay):
    pass


# class Border:
#     """Creates solid-color border around given frame."""

#     borderThickness = 0.05

#     def __init__(self, color: tuple):
#         self.color = color

#     def draw(self, frame: NDArray) -> NDArray:
#         """Returns edited image with border around it."""

#         frameWidth, frameHeight = frame.shape[0:2]

#         top = int(self.borderThickness * frameHeight)
#         bottom = top
#         left = int(self.borderThickness * frameWidth)
#         right = left

#         frame = cv2.copyMakeBorder(
#             frame,
#             top,
#             bottom,
#             left,
#             right,
#             borderType=cv2.BORDER_CONSTANT,
#             dst=None,
#             value=self.color,
#         )
#         return frame


# class Button:
#     """Contains static power button location parameters (top left corner and bottom right corner coordinates).

#     *(Called by drumGrid class in drumset.py)*"""

#     x1 = 0.025
#     x2 = 0.25
#     y1 = 0.025
#     y2 = 0.25


# class PowerButton(Button):
#     """Creates button denoting current state, which may be hit by user to change."""

#     powX = 0.045
#     powY = 0.125
#     subX = 0.045
#     subY = 0.185

#     def __init__(self, stateText: str, subText: str, color: tuple, textColor: tuple):

#         self.color = color
#         self.stateText = stateText
#         self.subText = subText
#         self.textColor = textColor

#     def draw(self, frame: NDArray) -> NDArray:
#         """Draws button and text onto the frame image."""

#         frameWidth, frameHeight = frame.shape[0:2]

#         tL = (int(self.x1 * frameWidth), int(self.y1 * frameHeight))
#         bR = (int(self.x2 * frameWidth), int(self.y2 * frameHeight))

#         frame = cv2.rectangle(frame, tL, bR, color=self.color, thickness=-1)
#         frame = cv2.putText(
#             frame,
#             self.stateText,
#             (int(self.powX * frameWidth), int(self.powY * frameHeight)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             fontScale=1,
#             color=self.textColor,
#             thickness=2,
#             lineType=cv2.LINE_AA,
#             bottomLeftOrigin=False,
#         )
#         frame = cv2.putText(
#             frame,
#             self.subText,
#             (int(self.subX * frameWidth), int(self.subY * frameHeight)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             fontScale=1,
#             color=self.textColor,
#             thickness=2,
#             lineType=cv2.LINE_AA,
#             bottomLeftOrigin=False,
#         )

#         return frame


# class titleText:
#     """Creates title and startup text on given frame."""

#     titleX1 = 0.35
#     titleY1 = 0.1
#     subtitleX1 = 0.4
#     subtitleY1 = 0.15

#     outBoxX1 = 0.2
#     outBoxY1 = 0.85
#     outBoxX2 = 0.8
#     outBoxY2 = 0.95
#     outTextX1 = 0.212
#     outTextY1 = 0.925

#     def draw(self, frame) -> NDArray:
#         """Draws title and startup message content onto frame image."""

#         frameWidth, frameHeight = frame.shape[0:2]

#         # "Invisible Drum_Kit" Title
#         frame = cv2.putText(
#             frame,
#             "Invisible Drum Kit",
#             (int(self.titleX1 * frameWidth), int(self.titleY1 * frameHeight)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             fontScale=1,
#             color=(0, 0, 0),
#             thickness=6,
#             lineType=cv2.LINE_AA,
#             bottomLeftOrigin=False,
#         )
#         frame = cv2.putText(
#             frame,
#             "Inspired by Rowan Atkinson",
#             (int(self.subtitleX1 * frameWidth), int(self.subtitleY1 * frameHeight)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             fontScale=1,
#             color=(0, 0, 0),
#             thickness=6,
#             lineType=cv2.LINE_AA,
#             bottomLeftOrigin=False,
#         )

#         # "Full Body Not in Frame" Message
#         tL = (int(self.outBoxX1 * frameWidth), int(self.outBoxY1 * frameHeight))
#         bR = (int(self.outBoxX2 * frameWidth), int(self.outBoxY2 * frameHeight))
#         frame = cv2.rectangle(frame, tL, bR, color=(0, 0, 200), thickness=-1)

#         frame = cv2.putText(
#             frame,
#             "Full Body Not In Frame",
#             (int(self.outTextX1 * frameWidth), int(self.outTextY1 * frameHeight)),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             fontScale=1,
#             color=(255, 255, 255),
#             thickness=6,
#             lineType=cv2.LINE_AA,
#             bottomLeftOrigin=False,
#         )

#         return frame
