from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TRIG=13
ECHO=12
NEO=7
RX=10
TX=11

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)
jk.mp3_set(RX,TX)
jk.mp3_volume(20)

while True:
	distance=jk.sonic_read(TRIG,ECHO)
	distance_map=jk.map_value(distance,0,50,0,100)
	
	jk.lcd_display(0,0,str(distance))
	jk.lcd_display(0,1,str(distance_map))
	jk.neopixel_bright(NEO,distance_map)
	
	if 0<distance<10:
		jk.neopixel_display_all(NEO,255,0,0)
		jk.mp3_play_time(4,1)
	elif 10<distance<20:
		jk.neopixel_display_all(NEO,255,255,0)
		jk.mp3_play_time(5,1)
	elif 20<distance<30:
		jk.neopixel_display_all(NEO,0,255,0)
		jk.mp3_play_time(6,1)
	elif 30<distance<40:
		jk.neopixel_display_all(NEO,128,0,128)
		jk.mp3_play_time(7,1)
	else:
		jk.neopixel_clear(NEO)
	
	jk.lcd_clear()
