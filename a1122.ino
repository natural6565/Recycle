#include <Adafruit_PWMServoDriver.h>
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN 150
#define SERVOMAX 600
#define USMIN 600
#define USMAX 2400
#define SERVO_FREQ 50
uint8_t servonum = 0;
 

int trigPin = 12;
int echoPin = 11;
bool st1, st2, st3;
int st3_cnt;
int kind; // 1 can 2 pls 3 gls 4 trsh, 큐로 구현해서 들어오면 추가하고 버리면 빼는 식으로 하는 게 좋을 듯?

// 모터 돌리는 함수

void mv(int n) {
  switch(n) {
    case 1:
      move1();
      break;
    case 2:
      move2();
      break;
    case 3:
      move3();
      break;
    case 4:
      move4(); 
  }
}

void move1() { //1번째 칸에 버리는 기준
  for(uint16_t pulselen = 275; pulselen < 490; pulselen++) { // 오른쪽 버리기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }
  
  delay(200);

  for(uint16_t pulselen = 490; pulselen > 275; pulselen--) { // 오른쪽 돌아오기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }

  for(uint16_t pulselen = 275; pulselen < 490; pulselen++) { // 오른쪽 버리기
    pwm.setPWM(2, 0, pulselen);
    delay(1);
  }

  delay(1000);

  for(uint16_t pulselen = 490; pulselen > 275; pulselen--) { // 오른쪽 돌아오기
    pwm.setPWM(2, 0, pulselen);
    delay(1);
  }
}

void move2() { //2번째 칸에 버리는 기준
  for(uint16_t pulselen = 275; pulselen < 490; pulselen++) { // 오른쪽 버리기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }
  
  delay(200);

  for(uint16_t pulselen = 490; pulselen > 275; pulselen--) { // 오른쪽 돌아오기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }

  for(uint16_t pulselen = 275; pulselen > 60; pulselen--) { // 왼쪽 버리기
    pwm.setPWM(2, 0, pulselen);
    delay(1);
  }

  delay(1000);

  for(uint16_t pulselen = 60; pulselen < 275; pulselen++) { // 왼쪽 돌아오기
    pwm.setPWM(2, 0, pulselen);
    delay(1);
  }
}

void move3() { //3번째 칸에 버리는 기준
  for(uint16_t pulselen = 275; pulselen > 60; pulselen--) { // 왼쪽 버리기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }
  
  delay(200);

  for(uint16_t pulselen = 60; pulselen < 275; pulselen++) { // 왼쪽 돌아오기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }

  for(uint16_t pulselen = 400; pulselen < 540; pulselen++) { // 오른쪽 버리기
    pwm.setPWM(1, 0, pulselen);
    delay(1);
  }

  delay(1000);

  for(uint16_t pulselen = 540; pulselen > 400; pulselen--) { // 오른쪽 돌아오기
    pwm.setPWM(1, 0, pulselen);
    delay(1);
  }
}

void move4() { //4번째 칸에 버리는 기준
  for(uint16_t pulselen = 275; pulselen > 60; pulselen--) { // 왼쪽 버리기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }
  
  delay(200);

  for(uint16_t pulselen = 60; pulselen < 275; pulselen++) { // 왼쪽 돌아오기
    pwm.setPWM(0, 0, pulselen);
    delay(1);
  }

  for(uint16_t pulselen = 400; pulselen > 190; pulselen--) { // 왼쪽 버리기
    pwm.setPWM(1, 0, pulselen);
    delay(1);
  }

  delay(1000);

  for(uint16_t pulselen = 190; pulselen < 400; pulselen++) { // 왼쪽 돌아오기
    pwm.setPWM(1, 0, pulselen);
    delay(1);
  }
}

void setup() {
  
  Serial.begin(9600);
  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);
  delay(10);
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  st1 = true;
  st2 = false;
  st3 = false;
}

void loop() {
  String result;
  if(st1) {
    long duration, distance;
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration = pulseIn(echoPin, HIGH);
    distance = 17 * duration / 1000;
    
    //Serial.println(distance);
    if((distance <= 20) == true) {
      Serial.println("1");
      st2 = true;
      st1 = false;
    }
    // Serial.println("9");
  }
  if(st2) {
    if(Serial.available()) {
      kind = Serial.read(); // 여기서 캔이냐 플라스틱이냐가 결정됨
      Serial.read();
        
      }
    // Serial.println("값 받음");
      st3 = true;
      st3_cnt = 0;
      st2 = false;
    }
    // Serial.println("2");
  
  if(st3) {
    // 모터 돌리는 함수 넣기
    mv(kind);
    st3 = false;
    st1 = true;
  }
    delay(100);
}
