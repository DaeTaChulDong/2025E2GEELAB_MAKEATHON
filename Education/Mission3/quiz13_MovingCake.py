from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
RX=10
TX=11
CDS=A0
NEO=7

jk.serial_connect(PORT)
jk.start()
jk.mp3_set(RX,TX)
jk.mp3_volume(30)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)
jk.lcd_set(0x27,16,2)

while():
	lux=jk.cds_read(CDS)
	jk.lcd_display(0,0,str(light))
	if light>=500:
		jk.neopixel_display_all(NEO,255,255,0)
		time.sleep(1)
		jk.neopixel_display_all(NEO,0,255,0)
		time.sleep(1)
		jk.mp3_play(2)
		time.sleep(2)
	else:
		jk.neopixel_clear(NEO)