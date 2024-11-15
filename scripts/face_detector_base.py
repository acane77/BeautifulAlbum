import cv2
import numpy as np

class FaceDetectorBase:
    def __init__(self):
        pass

    def __call__(self, image_path: str) -> [[float]]:
        pass

    def get_face_embedding(self, image_path: str) -> [[float]]:
        raise NotImplementedError()

    def visualize(self, image, rects):
        if type(image) == str:
            image = cv2.imread(image)
        for x, y, w, h in rects:
            cv2.rectangle(img=image, pt1=(x, y), pt2=(x + w, y + h), color=(0, 0, 255), thickness=2)
        cv2.imshow('result', image)
        cv2.waitKey(0)


