from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
NEO=7

jk.serial_connect(PORT)
jk.start()

jk.neopixel_set(NEO,4)
jk.neopixel_bright(NEO,20)
jk.neopixel_display_all(NEO,0,0,255)