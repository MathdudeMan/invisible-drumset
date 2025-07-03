import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
vid_pose = mp_pose.Pose()

class mp_landmarks:
    """Stores dictionary of body landmark locations for current frame."""

    def __init__(self, length: int):
        
        pointStructure = dict.fromkeys(['x','y','z','vis'], None)
        self.length = length
        self.rawData = None
        self.data = dict.fromkeys(range(self.length), pointStructure)

    def draw(self, frame):
        """Uses mediapipe library to draw landmarks inplace on current frame. 
        Uses input of only a given frame image, not requiring frame size parameters.
        
        *(Called by draw client in overlay.py.)*"""

        mp_drawing.draw_landmarks(frame, self.rawData, mp_pose.POSE_CONNECTIONS, 
                                landmark_drawing_spec = mp_drawing.DrawingSpec(color = (255,255,255), thickness = 2, circle_radius = 2), 
                                connection_drawing_spec = mp_drawing.DrawingSpec(color = (0,255,0), thickness = 2, circle_radius = 1))

    def update_data(self, image) -> None:
        """Updates current landmarks dictionary with input image."""

        allLandmarks = vid_pose.process(image)
        self.rawData = allLandmarks.pose_landmarks
        if self.rawData is not None:
            self._parse_coords(self.rawData)

    def _parse_coords(self, rawData: dict):

        for mark in range(self.length):

            coordinate = rawData.landmark[mark]
            self.data[mark] = {
                'x': coordinate.x,
                'y': coordinate.y,
                'vis': coordinate.visibility
                # 'z': markCoord.z,
                }