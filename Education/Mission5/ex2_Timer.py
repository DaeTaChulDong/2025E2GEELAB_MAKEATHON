from jikko.jikko import *
jk=Pyjikko()

PORT='COM4'

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
start_time=time.time()

while True:
	timer_value=time.time()-start_time
	jk.lcd_display(0,0,str(round(timer_value)))
	jk.lcd_clear()
