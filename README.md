# Invisible Drum Set App

Inspired by Rowan Atkinson's classic air drumming act, this Python app enables a user to play on their own invisible drum kit.

This application uses Mediapipe Pose, a Computer Vision library developed by Google for Pose Estimation, and OpenCV, a library for live video and image processing, to read and compute a user's hitting invisible drums. A "hit check" function calculates the event of hitting a drum with hand or foot based on body node locations defined within the library.

## Installation and Physical Setup

To use the app, clone the content in this repository or download as a .zip file, then run the `motion_project.exe` file in the folder.

`Repo clone`

Best practice requires the user to be seated on some stool or chair. The drum function may only be activated when all four torso nodes (shoulders and hips) are in frame. Thus, it is recommended that the user's webcam or external camera be set up at least 4-6 feet back from the stool position, allowing the full body of the player to fit in the camera frame.

## How It Works

The `motion_project.exe` file functions as a fullscreen window that mirrors the user via the computer's live built-in webcam. Drum "hits" are determined by calculating the real-time changes in angular velocity of each extremity (hands and feet) of the user. Imagine a drumstick in hand when doing so.

The "drum kit" is powered off by default. To activate the kit, perform the following:

1. Position the user's torso (i.e. both shoulders and hips) in the webcam frame.
2. With the app's video output as a guide, use any extremity to hit the "Power" button in the top left corner of the mirrored screen.

### Mediapipe Pose

Mediapipe Pose has 32 standard nodes it may detect from the human body. These are as follows:

![MediaPipe Nodes](https://camo.githubusercontent.com/d3afebfc801ee1a094c28604c7a0eb25f8b9c9925f75b0fff4c8c8b4871c0d28/68747470733a2f2f6d65646961706970652e6465762f696d616765732f6d6f62696c652f706f73655f747261636b696e675f66756c6c5f626f64795f6c616e646d61726b732e706e67)

You may find further documentation on the MediaPipe Pose library [here](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker).

### Hit Check

Each frame, the x, y, and visibility values are saved for each node in the torso and extremities (hands/feet). The hit check function then calculates the angle, angular velocity, and y-velocity for the extremity. If the angular/y - velocity values of the limb spike upwards, this registers a "hit."

When a hit is registered, the program then uses the location of that extremity in the camera view, relative to the rest of the body, to find what drum or cymbal in the kit was "hit." An appropriate drum or cymbal sound is triggered to match.

### Hit Grid

Within the program, this location mapping is done using a "hit grid." The hit grid holds the ranges of where a drum kit's components would be relative to a user's present static location in the camera frame, and it is recalculated framewise based on the positions of the user's torso nodes with the function "updateGrid()". See the following image for how this grid is mapped.

![Hit Grid]()

## Licensing

This app uses free and open source sound effects from freesound.com. The contributors of these sounds are as follows:

[Contrib A]()
[Contrib B]()
