import speech_recognition as sr
import sys
import threading
import time

r = sr.Recognizer()
mic = sr.Microphone()

stop_flag=False

def listen_command():  # 마이크로 음성 인식하고 문자열 반환
    with mic as source:
        r.adjust_for_ambient_noise(source)  # 소음 보정
        print("듣고 있습니다...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="ko-KR")
        print("인식된 음성: ", text)

        if "운동하자" in text:
            return "운동하자"
        elif "종료" in text:
            return "종료"
        else:
            return text
            
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
        return None
    except sr.RequestError as e:
        print("Google API 요청 실패:", e)
        return None
    finally:
        time.sleep(3)
    
def listen_loop(): #계속 돌아가면서 종료를 감지
    global stop_flag
    while True:
        cmd=listen_command()
        if cmd=="종료":
            print("종료 명령 감지. 프로그램 종료")
            sys.exit()
            
def listen_background():    #종료 감지를 위해서 백그라운드 스레드 실행
    thread=threading.Thread(target=listen_loop,daemon=True)
    thread.start()
    
#테스트 실행-단독 실행시
if __name__ == "__main__":
    print("음성 인식을 시작합니다. '운동하자'라고 말하면 감지됩니다. ")
    listen_background()
    while True:
        cmd=listen_command()
        if cmd=="운동하자":
            print("운동 시작 명령 감지")
        elif cmd=="종료":
            print("종료 명령 감지")
