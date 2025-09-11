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
	bright=jk.map_value(distance,0,50,0,100)
	
	jk.lcd_display(0,0,str(distance))
	jk.lcd_display(0,1,str(bright))
	
	jk.neopixel_bright(NEO,bright)
	
	if 5<distance<10:
		jk.neopixel_display_all(NEO,255,0,0)
		jk.mp3_play_time(8,2)
	elif 10<distance<15:
		jk.neopixel_display_all(NEO,255,128,0)
		jk.mp3_play_time(9,2)
	elif 15<distance<20:
		jk.neopixel_display_all(NEO,255,255,0)
		jk.mp3_play_time(10,2)
	elif 20<distance<25:
		jk.neopixel_display_all(NEO,0,255,0)
		jk.mp3_play_time(11,2)
	elif 25<distance<30:
		jk.neopixel_display_all(NEO,0,255,255)
		jk.mp3_play_time(12,2)
	elif 30<distacne<35:
		jk.neopixel_display_all(NEO,0,0,255)
		jk.mp3_play_time(13,2)
	else:
		jk.neopixel_display_all(NEO,255,0,255)
		jk.mp3_play_time(14,2)
		
	jk.lcd_clear()