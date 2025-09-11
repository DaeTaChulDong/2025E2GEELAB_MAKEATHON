from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,"hello")
	time.sleep(1)
	jk.lcd_clear()
	jk.lcd_display(1,0,"hello")
	time.sleep(1)
	jk.lcd_clear()
	jk.lcd_display(2,0,"hello")
	time.sleep(1)
	jk.lcd_clear()
	jk.lcd_display(3,0,"hello")
	time.sleep(1)

	jk.lcd_clear()
