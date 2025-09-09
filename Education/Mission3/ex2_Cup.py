from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
CDS=A0
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while():
	light=jk.cds_read(CDS)
	jk.lcd_display(0,0,str(light))
	
	if (200<light) & (light<600):
		jk.neopixel_display_all(NEO,0,0,255)
	time.sleep(1)
	jk.neopixel_clear(NEO)