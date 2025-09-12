from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
RX=10
TX=11
NEO=7
TRIG=13
ECHO=12

jk.serial_connect(PORT)
jk.start()

jk.mp3_set(RX,TX)
jk.mp3_volume(20)
jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while True:
	distance=jk.sonic_read(TRIG,ECHO)
	distance_map=jk.map_value(cds,0,50,0,100)
	
	jk.lcd_display(0,0,str(distance))
	jk.lcd_display(0,1,str(distance_map))
	jk.neopixel_bright(NEO,distance_map)
	
	if 0<=distance<=10:
		jk.neopixel_display_all(NEO,255,0,0)
		jk.mp3_play(1)
	elif 10<=distance<=20:
		jk.neopixel_display_all(NEO,255,255,0)
		jk.mp3_play(2)
	elif 20<=distance<=30:
		jk.neopixel_display_all(NEO,0,0,255)
		jk.mp3_play(3)
	elif 30<=distance<=40:
		jk.neopixel_display_all(NEO,0,255,0)
		jk.mp3_play(4)
	else:
		jk.neopixel_clear(NEO)
	
	jk.lcd_clear()
