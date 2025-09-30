import speech_recognition as sr
import sys
import threading
import time
import queue

class SpeechRecognitionThread:
    def __init__(self):
        self.r = sr.Recognizer()
        self.mic = None
        self.command_queue = queue.Queue()
        self.is_running = False
        self.thread = None
        
    def initialize_microphone(self):
        """마이크 초기화 (지연 초기화)"""
        if self.mic is None:
            print("마이크를 초기화합니다...")
            self.mic = sr.Microphone()
            print("마이크 초기화 완료")
    
    def start_listening(self):
        """음성 인식 스레드 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.thread.start()
        print("음성 인식 스레드 시작")
    
    def stop_listening(self):
        """음성 인식 스레드 중지"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        print("음성 인식 스레드 중지")
    
    def _listening_loop(self):
        """음성 인식 백그라운드 루프"""
        # 마이크 초기화
        self.initialize_microphone()
        
        while self.is_running:
            try:
                with self.mic as source:
                    self.r.adjust_for_ambient_noise(source)  # 소음 보정
                    print("듣고 있습니다...")
                    audio = self.r.listen(source, timeout=5, phrase_time_limit=5)

                try:
                    text = self.r.recognize_google(audio, language="ko-KR")
                    print("인식된 음성: ", text)

                    if "운동하자" in text:
                        self.command_queue.put("운동하자")
                    elif "종료" in text:
                        self.command_queue.put("종료")
                    else:
                        self.command_queue.put(text)
                        
                except sr.UnknownValueError:
                    print("음성을 인식할 수 없습니다.")
                    self.command_queue.put(None)
                except sr.RequestError as e:
                    print("Google API 요청 실패:", e)
                    self.command_queue.put(None)
                except sr.WaitTimeoutError:
                    self.command_queue.put(None)
                    
            except Exception as e:
                print(f"음성 인식 오류: {e}")
                time.sleep(1)
    
    def get_command(self, timeout=1.0):
        """명령어 가져오기 (논블로킹)"""
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def has_command(self):
        """대기 중인 명령어가 있는지 확인"""
        return not self.command_queue.empty()

# 전역 음성 인식 객체
speech_recognizer = SpeechRecognitionThread()

def start_speech_recognition():
    """음성 인식 시작"""
    speech_recognizer.start_listening()

def stop_speech_recognition():
    """음성 인식 중지"""
    speech_recognizer.stop_listening()

def get_voice_command():
    """음성 명령어 가져오기"""
    return speech_recognizer.get_command()

def has_voice_command():
    """음성 명령어가 있는지 확인"""
    return speech_recognizer.has_command()

# 직접 음성 인식 함수 (스레드 없이)
def listen_command_direct():
    """스레드 없이 직접 음성 인식"""
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("[SPEECH] 음성을 듣고 있습니다...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            
        try:
            text = r.recognize_google(audio, language="ko-KR")
            print(f"[SPEECH] 인식된 음성: {text}")
            
            if "운동하자" in text:
                return "운동하자"
            elif "종료" in text:
                return "종료"
            else:
                return text
                
        except sr.UnknownValueError:
            print("[SPEECH] 음성을 인식할 수 없습니다.")
            return None
        except sr.RequestError as e:
            print(f"[SPEECH] Google API 요청 실패: {e}")
            return None
            
    except sr.WaitTimeoutError:
        print("[SPEECH] 음성 입력 대기 시간 초과")
        return None
    except Exception as e:
        print(f"[SPEECH] 음성 인식 오류: {e}")
        return None

# 기존 함수 호환성을 위한 래퍼
def listen_command():
    """기존 함수와의 호환성을 위한 래퍼"""
    return listen_command_direct()

# 테스트 실행-단독 실행시
if __name__ == "__main__":
    print("음성 인식을 시작합니다. '운동하자' 또는 '종료'라고 말하면 감지됩니다.")
    
    start_speech_recognition()
    
    try:
        while True:
            cmd = get_voice_command()
            if cmd == "운동하자":
                print("운동 시작 명령 감지")
            elif cmd == "종료":
                print("종료 명령 감지")
                break
    except KeyboardInterrupt:
        print("프로그램 종료")
    finally:
        stop_speech_recognition()