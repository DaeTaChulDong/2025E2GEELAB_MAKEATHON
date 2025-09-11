from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TRIG=13
ECHO=12
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)

while True:
	distance=jk.sonic_read(TRIG,ECHO)
	bright=jk.map_value(distance,0,50,0,100)
	
	jk.lcd_display(0,0,str(distance))
	jk.lcd_display(0,1,str(bright))
	time.sleep(1)
	
	jk.neopixel_bright(NEO, bright)
	jk.neopixel_display_all(NEO,255,0,0)
	
	jk.lcd_clear()