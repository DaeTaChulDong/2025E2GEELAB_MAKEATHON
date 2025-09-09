from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
SERVO=8
TRIG=13
ECHO=12

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while():
	distance=jk.sonic_read(TRIG,ECHO)
	jk.lcd_display(0,0,str(distance))
	time.sleep(1)
	
	if distance<=10:
		jk.servo_degree(SERVO,90)
		jk.lcd_display(0,1,"open")
		time.sleep(5)
	else:
		jk.servo_degree(SERVO,0)
		
	jk.lcd_clear()