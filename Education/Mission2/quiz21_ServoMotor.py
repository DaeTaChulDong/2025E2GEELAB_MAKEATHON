from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'
SERVO=8

jk.serial_connect(PORT)
jk.start()

while True:
	jk.servo_degree(SERVO,0)
	time.sleep(1)
	jk.servo_degree(SERVO,90)
	time.sleep(1)
	jk.servo_degree(SERVO,180)

	time.sleep(1)
