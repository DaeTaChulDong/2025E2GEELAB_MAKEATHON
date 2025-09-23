import pyttsx3
import threading

class TTSManager:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # 말하기 속도
        self.engine.setProperty('volume', 0.9)  # 볼륨
        
        # 한국어 음성 설정 (시스템에 한국어 음성이 설치되어 있어야 함)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'korean' in voice.name.lower() or 'ko' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text):
        """텍스트를 음성으로 출력"""
        print(f"[TTS] {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def speak_async(self, text):
        """비동기적으로 텍스트를 음성으로 출력"""
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

# 전역 TTS 인스턴스
tts = TTSManager()

def speak(text):
    """간단한 TTS 함수"""
    tts.speak(text)

def speak_async(text):
    """비동기 TTS 함수"""
    tts.speak_async(text)
