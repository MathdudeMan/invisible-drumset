"""Includes tools for producing and storing video frames with OpenCV,
including camera and program window objects."""

import cv2
from numpy.typing import NDArray


class Camera:
    """Holds data for camera used."""

    CAPTURE_WIDTH_ID = 3
    CAPTURE_HEIGHT_ID = 4

    def __init__(self, port: int):

        self.cap = cv2.VideoCapture(port)

    def read(self) -> tuple[bool, NDArray]:

        return self.cap.read()

    def get_dimensions(self) -> tuple[int, int]:

        width = int(self.cap.get(self.CAPTURE_WIDTH_ID))
        height = int(self.cap.get(self.CAPTURE_HEIGHT_ID))

        return width, height

    def close(self):

        self.cap.release()
        cv2.destroyAllWindows
