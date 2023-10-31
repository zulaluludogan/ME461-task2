import time

try:
    import mediapipe as mp
except:
    print("Mediapipe should be installed. Running pip install mediapipe")
    try:
        from subprocess import run
        run(['pip','install','mediapipe'])
    except:
        print("pip install failed")
        raise ImportError
    
class MP_Controller:
    def __init__(self):
        
            self.hand_result = mp.tasks.vision.HandLandmarkerResult
            self.hand_landmarker = mp.tasks.vision.HandLandmarker
            self.createHandLandmarker()

        
            self.face_result = mp.tasks.vision.FaceLandmarkerResult
            self.face_landmarker = mp.tasks.vision.FaceLandmarker
            self.createFaceLandmarker()

    def createHandLandmarker(self):
        # callback function
        def update_result(
            hand_result: mp.tasks.vision.HandLandmarkerResult,
            output_image: mp.Image,
            timestamp_ms: int,
        ):
            self.hand_result = hand_result

        options_hands = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path="hand_landmarker.task"
            ),  # path to model
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # running on a live stream
            num_hands=1,  # track both hands
            min_hand_detection_confidence=0.5,  # lower than value to get predictions more often
            min_hand_presence_confidence=0.5,  # lower than value to get predictions more often
            min_tracking_confidence=0.5,  # lower than value to get predictions more often
            result_callback=update_result,
        )

        # initialize landmarker
        self.hand_landmarker = self.hand_landmarker.create_from_options(options_hands)

    def createFaceLandmarker(self):
        # callback function
        def update_result(
            face_result: mp.tasks.vision.FaceLandmarkerResult,
            output_image: mp.Image,
            timestamp_ms: int,
        ):
            self.face_result = face_result

        # HandLandmarkerOptions (details here: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker/python#live-stream)
        options_face = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path="face_landmarker.task"
            ),  # path to model
            running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,  # running on a live stream
            num_faces=1,
            min_face_detection_confidence=0.5,  # lower than value to get predictions more often
            min_face_presence_confidence=0.5,  # lower than value to get predictions more often
            min_tracking_confidence=0.5,  # lower than value to get predictions more often
            result_callback=update_result,
        )

        # initialize landmarker
        self.face_landmarker = self.face_landmarker.create_from_options(options_face)

    def detect_async(self, frame):
        # convert np frame to mp image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        # detect landmarks
        self.hand_landmarker.detect_async(
            image=mp_image, timestamp_ms=int(time.time() * 1000)
        )

        
        self.face_landmarker.detect_async(
            image=mp_image, timestamp_ms=int(time.time() * 1000)
        )

    def get_index_tip_coordinates(self):
        if self.hand_result.hand_landmarks != []:
            print(
                "HandLandmark.INDEX_FINGER_TIP result:\n {}".format(
                    self.hand_result.hand_landmarks[0][8]
                )
            )  # (HandLandmark.INDEX_FINGER_TIP=8)

            # GET INDEX_FINGER POSITION
            return (
                self.hand_result.hand_landmarks[0][8].x,
                self.hand_result.hand_landmarks[0][8].y
                # self.hand_result.hand_landmarks[0][8].z,
            )

    def get_mouth_coordinates(self):
        if self.face_result.face_landmarks != []:
            print(
                "FaceLandmark.upperMOUTH position:\n {}".format(
                    self.face_result.face_landmarks[0][13]
                )
            )  # (HandLandmark.INDEX_FINGER_TIP=8)
            print(
                "FaceLandmark.lowerMOUTH position:\n {}".format(
                    self.face_result.face_landmarks[0][14]
                )
            )  # (HandLandmark.INDEX_FINGER_TIP=8)
            return (
                (
                    self.face_result.face_landmarks[0][13].x,
                    self.face_result.face_landmarks[0][13].y
                ),
                (
                    self.face_result.face_landmarks[0][14].x,
                    self.face_result.face_landmarks[0][14].y
                )
                # self.face_result.face_landmarks[0][13].z,
            )  # GET MOUTH POSITION
        
    def get_nose_coordinates(self):
        if self.face_result.face_landmarks != []:
            print(
                "Nose position:\n {}".format(
                    self.face_result.face_landmarks[0][1]
                )
            )  # (HandLandmark.INDEX_FINGER_TIP=8)
            return(
                    self.face_result.face_landmarks[0][1].x,
                    self.face_result.face_landmarks[0][1].y
                )
                # self.face_result.face_landmarks[0][13].z, 
    def close(self):
        # close landmarker
        self.hand_landmarker.close()
        self.face_landmarker.close()

