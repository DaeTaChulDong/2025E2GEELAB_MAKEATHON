from jikko.jikko import *

jk=Pyjikko()

PORT='COM11'
TRIG=13
ECHO=12
TX=11
RX=10
NEO=7
TEM_HUM=4

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.mp3_set(RX,TX)
jk.mp3_volume(20)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while True:
	humi=jk.humi_read(TEM_HUM)
	distance=jk.sonic_read(TRIG,ECHO)
	
	jk.lcd_display(0,0,str(humi))
	jk.lcd_display(0,1,str(jk.temp_read(TEM_HUM)))
	jk.lcd_display(9,0,str(distance))
	
	if distance<20:
		if humi<40:
			jk.neopixel_display_all(NEO,255,0,0)
			jk.mp3_play(19)
			time.sleep(3)
		if humi>40:
			jk.neopixel_display_all(NEO,0,0,255)
			jk.mp3_play(20)
			time.sleep(3)
	jk.neopixel_clear(NEO)
	time.sleep(0.5)
	jk.lcd_clear()