# Invisible Drum Set App

Inspired by Rowan Atkinson's classic air drumming act, this Python app enables a user to play on their own invisible drum kit.

The app functions using Mediapipe Pose, a Pose Estimation library developed by Google, and OpenCV, a library for live video and image processing for Computer Vision (CV) applications. A "hitCheck" function in the program responds whenever a hand or foot performs a midair "Hit" with a drum sound appropriate to its relative location.

This app does not require extensive drum set experience, though some familiarity is recommended.

## Installation and Physical Setup

To use the app, clone the content in this repository or download and extract the .zip file, then run `drumset_app.exe`.

`git clone https://github.com/MathdudeMan/invisible-drumset`

The app is set by default to use the user's webcam (or the computer's primary camera port). The user should be seated on a stool or chair at least 4-6 feet away from the webcam, allowing the full body of the player to fit within the camera frame.

## How It Works

`drumset_app.exe` outputs a fullscreen window containing the mirrored webcam capture. Drum "hits" are determined by calculating the real-time changes in velocity of each extremity (hands and feet) of the user - a good down-up wrist snap should trigger this.

The app operates between three different states, controlled by screen presence and operation of the corner Power button:

1. User Offscreen ('Out'): This displays the message "User Not In Frame." Triggered when user torso exits the frame.
2. Power Off ('Off'): User onscreen, with audio inactive. Set automatically when user torso re-enters frame.
3. Power On ('On'): User onscreen with audio activated. Triggered from the Off state by "hitting" the button in the top-left corner.

The "drum kit" and associated audio is powered off by default. To activate the kit, perform the following:

1. Position the user's torso (i.e. both shoulders and hips) completely in the webcam frame.
2. With the app's video output as a guide, use any extremity to "hit" the "Power" button in the top left corner of the mirrored screen.

### Mediapipe Pose

**Mediapipe Pose** detects 32 standard nodes from the human body. The source code configures these as shown:

![MediaPipe Nodes](./assets/readme_images/Nodes_Edit.png)

Further documentation on MediaPipe Pose may be found [here](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker).

### Frame-by-Frame Analysis

For every frame, the x, y, and visibility (0 - 1) parameters for each node in the torso and extremities (hands/feet) are read and saved, alongside storing calculated values for extremity angle and vertical length. The program's "hit" algorithm is then run for each extremity, reacting when the angular or vertical velocity values of the limb have a sharp upward spike after downward motion.

For reference, extremity angles are calculated using the following degree plane:

![Degree Circle](./assets/readme_images/hitAngles.jpg)

When a hit is registered, the program uses a "hit grid" to map what drum or cymbal in the hypothetical drum kit was "hit." This hit grid holds row/column ranges based on the user's present location in the frame, which are then mapped to drum set components. The grid ranges are recalculated each frame based on the user's hip and shoulder locations. This method allows accurate drum mapping regardless of the location or size of the user in the frame.

#### Hit Grid (After Image Mirroring):

![Hit Grid](./assets/readme_images/Grid_Diagram.png)

Finally, the program uses the **playsound** library to output the drum audio mapped to the hit location. Note that there is a buffer built in to the **playsound** library, so audio playback for hits is not instant.

## Licensing

All sound effects in this app are obtained from from ![Freesound.org](https://freesound.org/), a repository for free and open source audio.

This project is copyright protected by the MIT License.
