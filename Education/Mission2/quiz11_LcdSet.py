from jikko.jikko import *

jk=Pyjikko()

#포트 번호 개별적으로 바꾸기
PORT='COM4'

jk.serial_connect(PORT)
jk.start()

jk.lcd_set(0x27,16,2)
jk.lcd_display(0,0,"Hello, jikko")