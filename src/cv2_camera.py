"""Includes tools for producing and storing video frames with OpenCV,
including camera and program window objects."""

import cv2
from numpy.typing import NDArray


class Window:
    """Window object for holding user-facing content."""

    def __init__(self, title: str, width: int, height: int):

        self.title = title
        self.width = width
        self.height = height
        cv2.namedWindow(self.title, cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow(self.title, self.width, self.height)

    def scale_to_screen(self, cam: "Camera", screenWidth: int, screenHeight: int):
        """Scale window so both height and width span the screen."""

        cam_width, cam_height = cam.get_dimensions()

        scale = max((screenWidth / cam_width), (screenHeight / cam_height))
        width = int(cam_width * scale)
        height = int(cam_height * scale)
        cv2.resizeWindow(self.title, width, height)

    def display_frame(self, frame) -> bool:
        """Returns True if window remains open after frame, False if closed."""

        scale_factor = max(
            (self.width / frame.shape[1]), (self.height / frame.shape[0])
        )
        frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)

        cv2.imshow(self.title, frame)

        # Frame buffer (Conditional is always False)
        if cv2.waitKey(2) == -2:
            pass

        # If window closed, end program activity. Responsible for ending program.
        if cv2.getWindowProperty(self.title, cv2.WND_PROP_VISIBLE) < 1:
            return False

        return True


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
