from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TEM_HUM=4
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)

while True:
	temp=jk.temp_read(TEM_HUM)
	humi=jk.humi_read(TEM_HUM)
	jk.lcd_display(0,0,str(temp))
	jk.lcd_display(0,1,str(humi))
	
	if humi>=60:
		jk.neopixel_display_all(NEO,0,0,255)
	else:
		jk.neopixel_clear(NEO)
		
	time.sleep(1)
	jk.lcd_clear()
	