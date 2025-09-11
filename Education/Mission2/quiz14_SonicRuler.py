from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'
TRIG=13
ECHO=12

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,"sonic ruler")
	jk.lcd_display(0,1,str(jk.sonic_read(TRIG,ECHO)))
	time.sleep(1)

	jk.lcd_clear()
