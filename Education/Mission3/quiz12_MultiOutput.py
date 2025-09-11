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
jk.mp3_volume(20)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)
jk.lcd_set(0x27,16,2)

while True:
	lux=jk.cds_read(CDS)
	jk.lcd_display(0,0,str(lux))
	if lux>500:
		jk.mp3_play(1)
		jk.neopixel_display_all(NEO,255,0,0)
		time.sleep(2)

	jk.neopixel_clear(NEO)
