from jikko.jikko import *
import random

jk=Pyjikko()

PORT='COM11'
TEM_HUM=4
CDS=A0
NEO=7
TX=11
RX=10
SOIL=A1
SERVO=8

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
start_time=time.time()
jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)
jk.mp3_set(RX,TX)
jk.mp3_volume(20)

while True:
	temp=jk.temp_read(TEM_HUM)
	cds=jk.cds_read(CDS)
	time=time.time()-start_time
	soil=jk.soil_read(SOIL)
	
	jk.lcd_display(0,0,str(temp))
	jk.lcd_display(0,1,str(soil))
	jk.lcd_display(9,0,str(cds))
	jk.lcd_display(9,1,str(round(time)))
	print(round(time))
	
	if cds>500:
		jk.neopixel_display_all(NEO,255,255,0)
	else:
		jk.neopixel_clear(NEO)
		
			if time>20:
			jk.mp3_play(random.randint(15,18))
			start_time=time.time()
	
	if soil>800:
		jk.servo_degree(SERVO,90)
		time.sleep(1)
	else:
		jk.servo_degree(SERVO,0)	
		time.sleep(1)
	
	time.sleep(1)
	jk.lcd_clear()