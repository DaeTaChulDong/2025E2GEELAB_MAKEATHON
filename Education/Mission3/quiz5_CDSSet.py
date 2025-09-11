from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
CDS=A0

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,str(jk.cds_read(CDS)))
	time.sleep(1)

	jk.lcd_clear()
