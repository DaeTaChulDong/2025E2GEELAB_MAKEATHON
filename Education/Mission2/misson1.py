from jikko.jikko import *

jk=Pyjikko()

PORT='COM4'

BUZZER=6
LED=5

jk.serial_connect(PORT)
jk.start()

while():
	jk.led_digital(LED,HIGH)
	jk.buzzer(BUZZER, 131,1)
	jk.buzzer(BUZZER, 147,1)
	jk.buzzer(BUZZER, 165,1)
	jk.buzzer(BUZZER, 175,1)
	jk.buzzer(BUZZER,196,1)
	
	jk.led_digital(LED,LOW)
	time.sleep(3)
	
