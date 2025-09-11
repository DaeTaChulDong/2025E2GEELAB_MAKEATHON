from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
SERVO=8
SOIL=A1

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	soil=str(jk.soil_read(SOIL))
	jk.lcd_display(0,0,soil)
	
	if soil>800:
		jk.servo_degree(SERVO,90)
		time.sleep(1)
	else:
		jk.servo_degree(SERVO,0)
		time.sleep(1)
	jk.lcd_clear()