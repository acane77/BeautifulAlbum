import cv2

def opencv_detection(image, config_file_path):
    # 创建一个级联分类器 加载一个.xml分类器文件 它既可以是Haar特征也可以是LBP特征的分类器
    face_detecter = cv2.CascadeClassifier(config_file_path)
    # 多个尺度空间进行人脸检测   返回检测到的人脸区域坐标信息
    rects = face_detecter.detectMultiScale(image=image, scaleFactor=1.1, minNeighbors=5)
    return rects

def face_detection(image):
    face_detection_config = r'../third_party/opencv/data/haarcascades/haarcascade_frontalface_default.xml'
    return opencv_detection(image, face_detection_config)

def visualize(image, rects):
    for x, y, w, h in rects:
        cv2.rectangle(img=image, pt1=(x, y), pt2=(x + w, y + h), color=(0, 0, 255), thickness=2)
    cv2.imshow('result', image)
    cv2.waitKey(0)

def test_face_detection():
    src = cv2.imread(r'../test_data/gitlacane.jpg')
    rects = face_detection(src)
    print(rects)
    visualize(src, rects)

if __name__ == '__main__':
    test_face_detection()
