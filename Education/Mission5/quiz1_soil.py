from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'
SOIL=A1

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,str(jk.soil_read(SOIL))
	time.sleep(1)
	jk.lcd_clear()