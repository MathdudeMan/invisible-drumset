from .body import Body
from .enums import State
from .cv2_drawing import DrawingClient

from numpy.typing import NDArray
import cv2

import logging

logging.basicConfig(level=logging.DEBUG)


class ImageProcessor:
    def __init__(self, camera_width: int, camera_height: int):

        self.drummer = Body(camera_width, camera_height)
        self.state = State.OFF
        self.drawing_client = DrawingClient()

    def process_frame(
        self, newFrame: NDArray, draw_landmarks: bool = True, is_image_mirrored=False
    ) -> NDArray:
        """Update body attributes for given frame and perform drawing and audio processing."""

        self.state = self.drummer.process_frame(newFrame, draw_landmarks)

        if is_image_mirrored:
            newFrame = cv2.flip(newFrame, 1)

        newFrame = self.drawing_client.draw_overlay(newFrame, self.state)

        logging.debug("State: " + str(self.state))

        return newFrame
