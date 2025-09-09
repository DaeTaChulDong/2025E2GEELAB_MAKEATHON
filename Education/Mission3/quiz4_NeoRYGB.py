from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while():
	jk.neopixel_display(NEO,0,255,0,0)
	time.sleep(1)
	jk.neopixel_display(NEO,1,255,255,0)
	time.sleep(1)
	jk.neopixel_display(NEO,2,0,255,0)
	time.sleep(1)
	jk.neopixel_display(NEO,3,0,0,255)
	time.sleep(1)
	jk.neopixel_clear(NEO)
	time.sleep(1)