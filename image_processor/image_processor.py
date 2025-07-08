from .body import Body
from .utils import State
from .drawing_utils.overlays import DrawingClient

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
        self,
        newFrame: NDArray,
        is_image_mirrored: bool = False,
        draw_landmarks: bool = True,
    ) -> NDArray:
        """Update body attributes for given frame and perform drawing and audio processing."""

        self.state = self.drummer.process_frame(newFrame, draw_landmarks)

        if is_image_mirrored:
            newFrame = cv2.flip(newFrame, 1)

        newFrame = self.drawing_client.draw_overlay(newFrame, self.state)

        logging.debug("State: " + str(self.state))

        return newFrame
