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
	humi=str(jk.humi_read(TEM_HUM))
	jk.lcd_display(0,0,str(jk.temp_read(TEM_HUM)))
	jk.lcd_display(0,1,humi)
	
	if 40<humi<60:
		jk.neopixel_display(NEO,0,0,0,255)
	elif 60<humi<80:
		jk.neopixel_display(NEO,0,0,0,255)
		jk.neopixel_display(NEO,1,0,0,255)
	elif 80<humi<90:
		jk.neopixel_display(NEO,0,0,0,255)
		jk.neopixel_display(NEO,1,0,0,255)
		jk.neopixel_display(NEO,2,0,0,255)
	elif 90<humi<96:
		jk.neopixel_display_all(NEO,0,0,255)
		
	time.sleep(1)
	jk.neopixel_clear(NEO)
	jk.lcd_clear()