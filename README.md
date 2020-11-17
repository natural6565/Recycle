# 자동 분리수거기
## Arduino와 Python을 이용해 객체 판별
### 프로젝트 구상
* 현재 일회용품의 사용량 증가로 인한 쓰레기가 무분별하게 증가하는 반면 재활용은 잘 이루어지지 않고 있습니다. 이러한 문제를 바탕으로 해결에 도움이 되고자 구상해봤습니다.

### 프로젝트 계획
* 딥러닝(yolov5 모델)을 통해 학습시킨 자료들을 바탕으로 객체를 판별하고 이를 Python과 Arduino의 통신을 통해 구동하도록 계획했습니다.
<img src="https://user-images.githubusercontent.com/69147201/99410618-098adb80-2936-11eb-8ce9-e34f78fe87b7.jpg">

### 시행착오
* Arduino와 Python의 통신
* Arduino Thread 미지원
* 미 투입 상황에 지속적인 객체 인식으로 인한 CPU 과부화
### 해결방안
* Arduino와 Python의 통신                              -> Serial 통신
* Arduino Thread 미지원                                -> 시분할
* 미 투입 상황에 지속적인 객체 인식으로 인한 CPU 과부화 -> 
