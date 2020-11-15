# s누르면 이미지 추출해서 detect 실행

import cv2
import subprocess

capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 416)

while True:
    ret, frame = capture.read()
    cv2.imshow("VideoFrame", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.IMREAD_UNCHANGED
        cv2.imwrite("cap1.png", frame)
        subprocess.run(
            'python ./yolov5/detect.py --source cap1.png --weight best012.pt --img 416 --conf 0.5', shell=True)

capture.release()
cv2.destroyAllWindows()
