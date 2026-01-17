import importlib
from face_detector_base import *

# def face_detection(image):
#     face_detection_config = r'../third_party/opencv/data/haarcascades/haarcascade_frontalface_default.xml'
#     return opencv_detection(image, face_detection_config)
#
#
# def test_face_detection():
#     src = cv2.imread(r'../test_data/gitlacane.jpg')
#     rects = face_detection(src)
#     print(rects)
#     visualize(src, rects)
#

def face_detection(detector: FaceDetectorBase, image_path: str):
    return detector(image_path)


def create_detector(detector_name: str, *args, **kwargs):
    module_name = detector_name + "_detector"
    pipeline_module = importlib.import_module(module_name)
    return pipeline_module.DetectorImpl(*args, **kwargs)

def test_face_detection(detector: FaceDetectorBase):
    src = '/home/acane/projects/acane77.github.io/album/test/gitlacane.jpg'
    rects = detector(image_path=src)
    detector.visualize(image=src, rects=rects)

if __name__ == '__main__':
    test_cases = [
        #[ 'opencv', [ '../third_party/opencv/data/haarcascades/haarcascade_frontalface_default.xml' ] ],
        [ 'deepface', [ 'yolov8' ] ],
    ]
    for test_case in test_cases:
        print("-- Testing {}".format(test_case[0]))
        print("     Creating with args:", test_case[1])
        detector = create_detector(test_case[0], *test_case[1])
        print("detector", detector)
        test_face_detection(detector=detector)
