from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)

while True:
	jk.lcd_display(0,0,"Hello")
	time.sleep(1)
	jk.lcd_clear()
	time.sleep(1)

