"""Contains tools for defining and operating the invisible drum kit."""

import os
import logging
import enum

from .drawing_utils.buttons import Button, PowerButton
from .body_parts import Node
from .audio import AudioDevice
from .utils import ExtremityType, Side


class Drums(enum.Enum):
    RIDE = 0
    TOM1 = 1
    TOM2 = 2
    HAT = 3
    HAT_OPEN = 4
    CRASH = 5
    FLOOR_TOM = 6
    SD = 7
    BD = 8
    SPECIAL1 = 9
    SPECIAL2 = 10
    BUTTON = 11
    AIR = 12


def average(x: float | int, y: float | int) -> float:
    """Calculate floating average of two values."""

    average = (x + y) / 2
    return average


class DrumGrid:
    """Contains basic parameters for drum kit grid boxes. Gridlines are defined in the x and y directions."""

    # Minimum left foot angle to activate an open hat sound
    open_hat_angle = 70

    # Grid layout mapped top to bottom, right hand side to left hand side
    grid_layout = [
        [Drums.SPECIAL2, Drums.SPECIAL1],
        [Drums.RIDE, Drums.TOM2, Drums.TOM1, Drums.HAT, Drums.CRASH],
        [Drums.FLOOR_TOM, Drums.SD, Drums.HAT, Drums.CRASH],
        [Drums.BD, Drums.HAT],
    ]

    assets_dir = os.path.join(os.getcwd(), "assets", "Used_Audio")
    drum_sound_paths = {
        Drums.RIDE: os.path.join(assets_dir, "ride-acoustic02.wav"),
        Drums.TOM1: os.path.join(assets_dir, "tom-acoustic01.wav"),
        Drums.TOM2: os.path.join(assets_dir, "tom-acoustic02.wav"),
        Drums.HAT: os.path.join(assets_dir, "hihat-acoustic01.wav"),
        Drums.HAT_OPEN: os.path.join(assets_dir, "hihat-dist02.wav"),
        Drums.CRASH: os.path.join(assets_dir, "crash-acoustic.wav"),
        Drums.FLOOR_TOM: os.path.join(assets_dir, "tom-rototom.wav"),
        Drums.SD: os.path.join(assets_dir, "snare-acoustic01.wav"),
        Drums.BD: os.path.join(assets_dir, "kick-classic.wav"),
        Drums.SPECIAL1: os.path.join(assets_dir, "clap-808.wav"),
        Drums.SPECIAL2: os.path.join(assets_dir, "cowbell-808.wav"),
        # State.OFF: os.path.join(assets_dir, "Cowbell.wav"),
        # State.ON: os.path.join(assets_dir, "Cowbell.wav"),
        Drums.BUTTON: os.path.join(assets_dir, "Cowbell.wav"),
    }

    def __init__(self, cam_width: int, cam_height: int):

        self.horizontal_gridlines = [] * (len(self.grid_layout) + 1)
        self.vertical_gridlines = [] * (len(self.grid_layout))

        self.endX = cam_width
        self.endY = cam_height

        self.powButton = Button()
        self.powButton.x1 *= self.endX
        self.powButton.x2 *= self.endX
        self.powButton.y1 *= self.endY
        self.powButton.y2 *= self.endY

        self.audio_device = AudioDevice()
        self.sound_active = False

        self.hihat_open = False

    def draw_grid(self):
        pass

    def draw_button(self):
        pass

    def set_hihat_open(self, is_open: bool):
        self.hihat_open = is_open

    def update_gridlines(
        self, leftShoulder: Node, rightShoulder: Node, leftHip: Node, rightHip: Node
    ):
        """Uses body torso to update gridline locations."""

        # Calculate vertical references
        shoulderY = average(leftShoulder.y, rightShoulder.y)
        waistY = average(leftHip.y, rightHip.y)
        torsoHeight = waistY - shoulderY
        torsoDiv = (1 / 3) * torsoHeight

        # Calculate horizontal references
        waistLength = leftHip.x - rightHip.x
        torsoSplitX = average(leftHip.x, rightHip.x)

        # Calculate horizontal gridlines, from Top to Bottom
        self.horizontal_gridlines = [
            0,
            shoulderY - torsoDiv,
            waistY - torsoDiv,
            waistY + torsoDiv,
            self.endY,
        ]

        # Calculate vertical gridlines within each row, Top to Bottom and Right to Left (based on gridLayout)
        self.vertical_gridlines = [
            [0, torsoSplitX, self.endX],
            [
                0,
                rightShoulder.x - waistLength,
                rightShoulder.x,
                leftHip.x,
                leftShoulder.x + waistLength,
                self.endX,
            ],
            [
                0,
                rightShoulder.x,
                leftShoulder.x,
                leftShoulder.x + waistLength,
                self.endX,
            ],
            [0, torsoSplitX, self.endX],
        ]

    def get_location_id(self, extremity, img_mirrored: bool) -> Drums:
        """Determines present map id of limb. Calculates location and returns the associated string identifier."""

        x = extremity.head.x
        y = extremity.head.y

        if not (0 < x < self.endX and 0 < y < self.endY):
            return Drums.AIR

        # Auto-map feet
        if extremity.type == ExtremityType.FOOT and extremity.side == Side.LEFT:
            return Drums.HAT
        elif extremity.type == ExtremityType.FOOT and extremity.side == Side.RIGHT:
            return Drums.BD

        # Check for button hit
        buttonCheckX = False
        if img_mirrored:
            buttonCheckX = (
                (self.endX - self.powButton.x1) > x > (self.endX - self.powButton.x2)
            )
        else:
            buttonCheckX = self.powButton.x1 < x < self.powButton.x2

        if buttonCheckX and self.powButton.y1 < y < self.powButton.y2:
            return Drums.BUTTON

        mapVal = self._map_to_grid(x, y)

        # Open Hi Hat when left foot angled upwards
        if mapVal == Drums.HAT and self.hihat_open:
            mapVal = Drums.HAT_OPEN

        return mapVal

    def play_drum(self, extremity, mapVal: Drums):

        isHit = extremity.check_hit()
        if isHit is False:
            return

        # FIXME Image mirror
        mapVal = self.get_location_id(extremity, True)

        if mapVal == "":
            return
        elif mapVal == Drums.BUTTON:
            self._triggerButton()
        elif self.sound_active:
            self._triggerAudio(mapVal)

    def _map_to_grid(self, xLoc: float, yLoc: float) -> Drums:
        """Maps row and column of extremity head and returns the associated string identifier."""

        rowMap = 0
        colMap = 0

        for i in range(len(self.horizontal_gridlines) - 1):
            if self.horizontal_gridlines[i] <= yLoc <= self.horizontal_gridlines[i + 1]:
                rowMap = i
                break

        for j in range(len(self.vertical_gridlines[rowMap]) - 1):
            if (
                self.vertical_gridlines[rowMap][j]
                <= xLoc
                <= self.vertical_gridlines[rowMap][j + 1]
            ):
                colMap = j
                break

        logging.debug("x: " + str(xLoc) + ", y: " + str(yLoc))
        logging.debug("Row: " + str(rowMap) + ", Col: " + str(colMap))
        logging.debug(self.grid_layout[rowMap][colMap])

        return self.grid_layout[rowMap][colMap]

    def _triggerButton(self):
        """Trigger audio of button"""

        self.sound_active = not self.sound_active
        self._triggerAudio(Drums.BUTTON)

    def _triggerAudio(self, mapVal: Drums):

        self.audio_device.play_audiofile(self.drum_sound_paths[mapVal])
