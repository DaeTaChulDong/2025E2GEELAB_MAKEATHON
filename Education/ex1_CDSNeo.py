from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
CDS=A0
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)

while():
	lux=jk.cds_read(pin)
	jk.lcd_display(0,0,str(light))
	if lux<200:
		jk.neopixel_clear(NEO)
		time.sleep(1)
	elif 200<=lux<400:
		jk.neopixel_display(NEO,0,255,255,255)
		jk.neopixel_display(NEO,1,255,255,255)
		time.sleep(1)
	else:
		jk.neopixel_display_all(NEO,0,255,0)
		time.sleep(1)
	jk.neopixel_clear(NEO)