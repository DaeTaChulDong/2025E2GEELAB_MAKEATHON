# 2025E2GEELAB_MAKEATHON

# 기본 연결
from jikko.jikko import *

jk=Pyjikko()

PORT='COM4' //포트 번호는 따로 확인하여 연결

jk.serial_connect(PORT)

jk.start()

# LED와 부저(빛 On/Off 출력, 원하는 계이름 연주)
LED=5 //예시
BUZZER=6 //예시

jk.led_digital(pin,write) //LED에 연결, 온오프 코드
jk.led_digital(LED,HIGH) //위 코드 예시, HIGH/LOW

jk.buzzer(pin,tone,time)
jk.buzzer(BUZZER,131,1) //위 코드 예시, 도 연주

while True:
  jk.led_digital(LED,HIGH)
  jk.buzzer(BUZZER,131,1)
  jk.led_digital(LED,LOW)
  time.sleep(2) 
//LED를 켜고 도 연주 후 LED를 끄고 2초 뒤 다시 시작하는 예시 코드

# 초음파센서와 LCD(LCD:글자 display, 초음파센서:반사 초음파로 거리 측정)
jk.lcd_set(address,x,y) //LCD를 사용하기 전 세팅 코드
jk.lcd_set(0x27,16,2) //위 코드 예시

jk.lcd_display(x,y,test)
jk.lcd_display(0,0,"Hello") //위 코드 예시 둘째 줄이면 y=1

jk.lcd_clear() //LCD 화면 초기화

jk.sonic_read(trg,eco) //trig핀번호, echo핀번호
jk.sonic_read(13,12) //위 코드 예시

while True:
  jk.lcd_display(0,0,"sonic_read")
  jk.lcd_display(0,1,str(jk.sonic_read(TRIG,ECHO)))
  time.sleep(1)
  jk.lcd_clear()
  //LCD(0,0)에는 sonic_ruler 글자를 표현하고 LCD(0,1)에 1초에 한 번씩 초음파센서값을 출력하는 코드

# 서보모터(서보모터를 원하는 각도로 움직일 수 있음)
jk.servo_degree(pin,write) //연결된 핀번호, 서보모터 각도(0~180)
jk.servo_degree(SERVO,90) //예시 코드

time.sleep(1) //서보모터 코드 이후 time.sleep코드 필요

# 네오픽셀(네오픽셀:RGB로 여러 색 표현)
jk.neopixel_set(pin,num) //네오픽셀 사용 전 세팅 코드: 핀번호, LED 개수
jk.neopixel_set(7,4) //7핀에 4개 LED 연결
jk.neopixel_bright(pin, bright) //bright:LED 밝기(0~255)

jk.neopixel_display_all(pin,r,g,b) //네오픽셀에 연결된 모든 LED의 색을 조절하는 코드
jk.neopixel_display_all(pin,NeoColor.RED) //패키지 내 변수 이용
jk.neopixel)display_all(pin,color) //미리 선언한 3개의 색상값이 담긴 튜플 이용하여 표현도 가능

jk.neopixel_display(pin,who,r,g,b) //who:색을 출력할 LED(0~3)

jk.neopixel_clear(pin) //네오픽셀 모두 끄기

# 조도센서(CDS): 빛의 밝기에 따라 값이 변하는 소자(0~1023)
jk.cds_read(pin) //조도센서 값을 읽는 코드, pin은 A0, A1 사용

# 스피커와 MP3 모듈(저장된 MP3 음원파일 재생)
jk.mp3_set(rx,tx) //mp3 모듈의 rx핀, tx핀
jk.mp3_set(10,11)

jk.mp3_volume(vol) //볼륨 조절 코드(0~30)

jk.mp3_play(play) //지정한 음성 파일 재생, play:재생할 음성 파일 번호
jk.mp3_play_time(play,sec) //지정한 음성 파일을 지정한 시간만큼 재생

jk.mp3_stop() //MP3 모듈 재생 정지
//네오픽셀 실행코드 이후 MP3 실행코드를 작성할 것


# 매핑 기능(데이터의 값 범위를 비례하게 변환)
jk.map_value(val_in,a_min,a_max,b_min,b_max) //a->b 변환

while True:
  distance=jk.sonic_read(TRIG,ECHO)
  distance_map=str(jk.map_value(distance,0,50,0,255)
//초음파센서값을 매핑하는 예시 코드

# 온습도 센서: temp,humi
jk.temp_read(pin)
jk.humi_read(pin)
//온습도 센서 이용하여 각각 온도/습도 값 읽기
jk.lcd_display(0,0,str(jk.temp_read(TEM_HUM))) //LCD첫째줄에 온도 표시

# 토양수분센서(토양의 수분량을 측정)
jk.soil_read(pin) //토양수분센서가 연결된 핀번호

jk.soil_read(A1) //직코에서는 A1에 연결되어 있기 때문에 A1을 입력

# 타이머와 난수
time.time() //현재 시간을 초 단위로 반환하는 코드

start_time=time.time() //시작 시간 측정

timer_value=time.time()-start.time //실행에 걸린 시간 측정

start_time=time.time() //타이머 초기화

jk.lcd_display(0,0,str(round(timer_value))) //반올림하여 정수로 변환한 뒤 문자열 반환하여 LCD에 출력하기

//난수 코드를 사용하기 위해 
import random

random.randint(a,b) //a와 b 사이 임의의 정수 반환
random.randint(1,10) //1에서 10 사이 임의의 정수 반환

