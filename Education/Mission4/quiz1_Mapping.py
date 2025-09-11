from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TRIG=13
ECHO=12

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	distance=jk.sonic_read(TRIG,ECHO)
	distance_map=jk.map_value(distance,0,50,0,255)
	
	jk.lcd_display(0,0,str(distance))
	jk.lcd_display(0,1,str(distance_map))
	
	time.sleep(1)
	jk.lcd_clear()