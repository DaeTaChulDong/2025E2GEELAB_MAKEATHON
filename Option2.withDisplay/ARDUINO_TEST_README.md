# 아두이노 통신 테스트 가이드

## 개요
이 프로젝트는 ArduinoCommunication.py 라이브러리를 사용하여 아두이노와 Python 간의 시리얼 통신을 테스트하는 코드입니다.

## 파일 구성

### 1. ArduinoExerciseController.ino
- 아두이노에 업로드할 스케치 파일
- LED, 사운드, MP3 제어 기능 포함
- Python에서 받은 명령을 실행하고 결과를 시리얼로 전송

### 2. arduino_test.py
- 종합적인 아두이노 통신 테스트 코드
- LED, 사운드, 음성 안내, MP3 재생 테스트
- 실제 운동 프로그램과 유사한 시퀀스 테스트

### 3. arduino_monitor.py
- 아두이노에서 오는 메시지를 실시간으로 모니터링
- 디버깅 및 통신 상태 확인용

## 하드웨어 연결

### 아두이노 핀 연결
```
LED 연결:
- 녹색 LED: 13번 핀
- 노란색 LED: 12번 핀  
- 빨간색 LED: 11번 핀
- 공통 GND

스피커/부저:
- 부저: 8번 핀
- GND
```

### 회로도
```
Arduino Uno
├── 13번 핀 → 녹색 LED → 220Ω 저항 → GND
├── 12번 핀 → 노란색 LED → 220Ω 저항 → GND
├── 11번 핀 → 빨간색 LED → 220Ω 저항 → GND
├── 8번 핀 → 부저(+)
└── GND → 부저(-)
```

## 사용 방법

### 1. 아두이노 설정
1. ArduinoExerciseController.ino 파일을 아두이노 IDE에서 열기
2. 아두이노에 업로드
3. 시리얼 모니터에서 "Arduino Exercise Controller Ready" 메시지 확인

### 2. Python 테스트 실행

#### 종합 테스트
```bash
python arduino_test.py
```

#### 실시간 모니터링
```bash
python arduino_monitor.py
```

### 3. 포트 설정
코드에서 COM 포트를 환경에 맞게 수정:
```python
# arduino_test.py와 arduino_monitor.py에서
if not initialize_arduino('COM3'):  # 여기를 수정
```

일반적인 포트:
- Windows: COM3, COM4, COM5, COM6
- Linux: /dev/ttyUSB0, /dev/ttyACM0
- Mac: /dev/cu.usbserial-xxxx

## 지원하는 명령어

### LED 제어
- `LED:green` - 녹색 LED 켜기
- `LED:yellow` - 노란색 LED 켜기
- `LED:red` - 빨간색 LED 켜기
- `LED:blue` - 파란색 (노란색으로 대체)
- `LED:off` - 모든 LED 끄기

### 사운드 제어
- `SOUND:start` - 시작 사운드
- `SOUND:success` - 성공 사운드
- `SOUND:fail` - 실패 사운드
- `SOUND:clap` - 박수 사운드
- `SOUND:complete` - 완료 사운드

### 음성 안내
- `VOICE:welcome` - 환영 메시지
- `VOICE:follow_me` - 따라하기 안내
- `VOICE:success` - 성공 안내
- `VOICE:fail` - 실패 안내
- `VOICE:complete` - 완료 안내
- `VOICE:goodbye` - 작별 인사

### MP3 재생
- `MP3:0001` ~ `MP3:0200` - 특정 MP3 파일 재생
- 현재는 시뮬레이션으로 다른 주파수의 사운드 재생

## 예상 출력

### 아두이노 시리얼 모니터
```
Arduino Exercise Controller Ready
Commands: LED:green/yellow/red/off, SOUND:start/success/fail/clap, MP3:filename
Executing: LED:green
LED: Green ON
Command executed successfully
---
```

### Python 콘솔
```
아두이노 통신 테스트 시작
==================================================
아두이노 연결 시도...
아두이노 연결 성공!

=== LED 제어 테스트 ===
LED green 켜기...
아두이노에 명령 전송: LED:green
MP3 재생: 0001
...
```

## 문제 해결

### 연결 실패
1. 아두이노가 올바른 포트에 연결되어 있는지 확인
2. 아두이노 드라이버가 설치되어 있는지 확인
3. 다른 프로그램에서 시리얼 포트를 사용하고 있지 않은지 확인

### 명령이 실행되지 않음
1. 아두이노 시리얼 모니터에서 명령이 수신되는지 확인
2. baudrate가 9600으로 설정되어 있는지 확인
3. 아두이노 스케치가 올바르게 업로드되었는지 확인

### MP3 재생이 안됨
- 현재는 시뮬레이션으로 구현됨
- 실제 MP3 모듈(DFPlayer Mini 등) 연결 시 해당 코드 활성화 필요

## 확장 가능성

1. **실제 MP3 모듈 연결**: DFPlayer Mini 등과 연결하여 실제 음성 파일 재생
2. **센서 추가**: 가속도계, 자이로스코프 등으로 동작 감지
3. **디스플레이 추가**: LCD나 OLED로 상태 표시
4. **무선 통신**: WiFi나 Bluetooth 모듈 추가

## 라이센스
이 프로젝트는 교육 및 연구 목적으로 제작되었습니다.
