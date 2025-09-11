from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM11'

LED=5

jk.serial_connect(PORT)
jk.start()

while True:
	jk.led_pwm(LED,200)
	time.sleep(1)
	jk.led_pwm(LED,100)
	time.sleep(1)
	jk.led_pwm(LED,10)

	time.sleep(1)
