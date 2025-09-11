from jikko.jikko import *
jikko=Pyjikko()

PORT='COM4'
RX=10
TX=11

jk.serial_connect(PORT)
jk.start()
jk.mp3_set(RX,TX)
jk.mp3_volume(20)

while True:
	jk.mp3_play(1)

	time.sleep(3)
