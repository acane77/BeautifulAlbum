from face_detector_base import *
import cv2


class OpenCVDetector(FaceDetectorBase):
    def __init__(self, config_file_path = ""):
        super(OpenCVDetector, self).__init__()
        if (config_file_path == ""):
            config_file_path = r'../third_party/opencv/data/haarcascades/haarcascade_frontalface_default.xml'
        # 创建一个级联分类器 加载一个.xml分类器文件 它既可以是Haar特征也可以是LBP特征的分类器
        self._face_detecter = cv2.CascadeClassifier(config_file_path)

    def __call__(self, image_path: str) -> [[float]]:
        # 多个尺度空间进行人脸检测   返回检测到的人脸区域坐标信息
        image = cv2.imread(image_path)
        rects = self._face_detecter.detectMultiScale(image=image, scaleFactor=1.1, minNeighbors=5)
        return rects

DetectorImpl = OpenCVDetector