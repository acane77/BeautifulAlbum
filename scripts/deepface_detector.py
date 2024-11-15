from face_detector_base import *
from deepface import DeepFace

backends = [
  'opencv',
  'ssd',
  'dlib',
  'mtcnn',
  'fastmtcnn',
  'retinaface',
  'mediapipe',
  'yolov8',
  'yunet',
  'centerface',
]

class DeepfaceDetector(FaceDetectorBase):
    def __init__(self, backend = ""):
        super(DeepfaceDetector, self).__init__()
        if backend == "":
            backend = "yolov8"
        if backend not in backends:
            raise Exception("invalid backend: {}, supported backends: {}".format(backends, ", ".join(backends)))
        self._model = backend

    def __call__(self, image_path: str) -> [[float]]:
        # face detection and alignment
        try:
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self._model,
                align=False,
                enforce_detection=False
            )
        except ValueError as ex:
            print("-- DeepfaceDetector WARNING: {}".format(str(ex)))
            face_objs = []
        return [ [ face['facial_area']['x'], face['facial_area']['y'],
                   face['facial_area']['w'], face['facial_area']['h']]
                 for face in face_objs if face["confidence"] > 0.5 ]

DetectorImpl = DeepfaceDetector