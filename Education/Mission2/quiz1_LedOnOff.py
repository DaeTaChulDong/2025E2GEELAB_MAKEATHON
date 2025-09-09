from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM11'

LED=5

jk.serial_connect(PORT)
jk.start()

i=0
while(i<3):
	#LED 켜기
	jk.led_digital(LED,HIGH)
	time.sleep(1)
	#LED 끄기
	jk.led_digital(LED,LOW)
	time.sleep(1)
	i++