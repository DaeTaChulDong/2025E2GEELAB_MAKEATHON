import speech_recognition as sr
import sys
import threading
import time

r = sr.Recognizer()
mic = sr.Microphone()

stop_flag = False
background_thread = None

def listen_command():  # 마이크로 음성 인식하고 문자열 반환
    with mic as source:
        r.adjust_for_ambient_noise(source)  # 소음 보정
        print("듣고 있습니다...")
        audio = r.listen(source, timeout=1, phrase_time_limit=3)

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
    except sr.WaitTimeoutError:
        return None
    
def listen_loop():  # 계속 돌아가면서 종료를 감지
    global stop_flag
    while not stop_flag:
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("(배경에서 듣고 있습니다...)")
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
                
            text = r.recognize_google(audio, language="ko-KR")
            print(f"배경 인식: {text}")
            
            if "종료" in text:
                print("종료 명령 감지. 프로그램 종료")
                stop_flag = True
                sys.exit()
                
        except sr.UnknownValueError:
            pass  # 무음이거나 인식 실패시 계속 진행
        except sr.WaitTimeoutError:
            pass  # 타임아웃시 계속 진행
        except sr.RequestError as e:
            print("Google API 요청 실패:", e)
            time.sleep(1)
        except Exception as e:
            print(f"음성 인식 오류: {e}")
            time.sleep(1)
            
def listen_background():  # 종료 감지를 위해서 백그라운드 스레드 실행
    global background_thread, stop_flag
    stop_flag = False
    background_thread = threading.Thread(target=listen_loop, daemon=True)
    background_thread.start()
    print("배경 음성 인식 스레드가 시작되었습니다.")
    
def stop_listening():  # 배경 스레드 중지
    global stop_flag
    stop_flag = True
    print("배경 음성 인식 스레드를 중지합니다.")
    
# 테스트 실행-단독 실행시
if __name__ == "__main__":
    print("음성 인식을 시작합니다. '운동하자'라고 말하면 감지됩니다.")
    listen_background()
    while True:
        cmd = listen_command()
        if cmd == "운동하자":
            print("운동 시작 명령 감지")
        elif cmd == "종료":
            print("종료 명령 감지")
            break
