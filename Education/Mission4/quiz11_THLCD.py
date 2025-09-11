from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
TEM_HUM=4

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,str(jk.temp_read(TEM_HUM)))
	jk.lcd_display(0,1,str(jk.humi_read(TEM_HUM)))
	
	time.sleep(1)
	jk.lcd_clear()