from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TEM_HUM=4
CDS=A0
NEO=7
SOIL=A1
SERVO=8

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while True:
	temp=str(jk.temp_read(TEM_HUM))
	humi=str(jk.humi_read(TEM_HUM))
	soil=str(jk.soil_read(SOIL))	
	light=jk.cds_read(CDS)
	
	jk.lcd_display(0,0,temp)
	jk.lcd_display(0,0,humi)
	
	if light>500:
		jk.neopixel_display_all(NEO,255,255,0)
	else:
		jk.neopixel_clear(NEO)
		
	if soil>800:
		jk.servo_degree(SERVO,90)
		time.sleep(1)
	else:
		jk.servo_degree(SERVO,0)
		time.sleep(1)
	
	jk.lcd_clear()