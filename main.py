from peripherals.camera import Camera
from peripherals.window import Window
from image_processor.image_processor import ImageProcessor

import tkinter as tk
import logging

root = tk.Tk()
SCREEN_WIDTH = int(root.winfo_screenwidth())  # 1920
SCREEN_HEIGHT = int(root.winfo_screenheight())  # 1440
root.withdraw()

CAMERA_PORT = 0


class DrumsetApp:

    def __init__(self):

        # initialize camera
        self.cam = Camera(CAMERA_PORT)
        self.mirror_output = True

        self.window_title = "Motion Cap"
        self.window = Window(self.window_title, SCREEN_WIDTH, SCREEN_HEIGHT)

        camera_width, camera_height = self.cam.get_dimensions()
        self.image_processor = ImageProcessor(camera_width, camera_height)

    def run(self):
        """Run main app loop."""

        self.enabled = True

        while self.enabled:

            # Get frame
            img_success, newFrame = self.cam.read()
            if not img_success:
                logging.error("No image from camera")
                self.enabled = False
                break

            # Process frame and generate audio
            newFrame = self.image_processor.process_frame(
                newFrame, is_image_mirrored=self.mirror_output
            )

            # Display frame
            self.enabled = self.window.display_frame(newFrame)

        self.cam.close()


if __name__ == "__main__":

    newApp = DrumsetApp()
    newApp.run()
