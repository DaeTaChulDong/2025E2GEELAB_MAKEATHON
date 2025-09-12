from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
SOIL=A1
CDS=A0
TEM_HUM=4
SERVO=8
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)

while True:
	T=jk.temp_read(TEM_HUM)
	H=jk.humi_read(TEM_HUM)
	soil=jk.soil_read(SOIL)
	
	jk.lcd_display(0,0,str(T))
	jk.lcd_display(0,1,str(H))
	
	if jk.cds_read(CDS)>500:
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
