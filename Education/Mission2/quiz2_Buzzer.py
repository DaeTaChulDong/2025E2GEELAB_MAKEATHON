from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'

BUZZER=6

jk.serial_connect(PORT)
jk.start()

#부저 울리기(pin,tone,type): pin 개별적으로 바꾸기
while True:
	jk.buzzer(BUZZER,131,1)
	time.sleep(1)
	jk.buzzer(BUZZER,147,1)
	time.sleep(1)
	jk.buzzer(BUZZER,165,1)
	time.sleep(1)
	jk.buzzer(BUZZER,175,1)

	time.sleep(1)
