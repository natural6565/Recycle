# 시리얼에서 1받으면 detect 실행

import serial
import cv2
import subprocess

print('serial'+serial.__version__)

# set a port number & baud rate
PORT = 'COM3'  # 아두이노 연결후 몇번 포트로 연결되는지 확인하고 적어야댐
BaudRate = 9600

ARD = serial.Serial(PORT, BaudRate)  # 시리얼 통신을 위한 설정, 선언

isDetect = False


def Decode(A):  # 시리얼 한줄 읽은 후 결과 리턴
    A = A.decode().strip()
    print(A)
    if A == '1':
        return True
    else:
        return False


def Ardread():  # ARD 읽어서 Decode 실행 후 결과 리턴
    global isDetect
    cur = ARD.readline()
    if cur:
        LINE = cur
        if Decode(LINE) and not isDetect:
            isDetect = True
            cv2.IMREAD_UNCHANGED
            cv2.imwrite("cap1.png", frame)
            subprocess.run(
                'python ./yolov5/detect.py --source cap1.png --weight cgp.pt --img 416 --conf 0.5', shell=True)
            isDetect = False
            return True
        else:
            return False


# 0은 기본 웹캠을 의미, 두번째 인자는 async관련 warn제거를 위해 넣음
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 416)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 416)

while True:
    # frame만으로 detect.py의 소스로 넘겨줄 수 있나?
    ret, frame = capture.read()
    cv2.imshow("VideoFrame", frame)
    Ardread()
    if cv2.waitKey(1) == ord('q'):  # q 입력시 종료
        break

# 카메라 할당 메모리 해제, 윈도우창 닫음
capture.release()
cv2.destroyAllWindows()
