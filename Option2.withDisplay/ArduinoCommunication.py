import serial
import time
import threading
import random

class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        """
        아두이노와의 시리얼 통신을 담당하는 클래스
        port: 시리얼 포트 (Windows: COM3, COM4 등, Linux/Mac: /dev/ttyUSB0 등)
        baudrate: 통신 속도 (아두이노 코드와 일치해야 함)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.is_connected = False
        
    def connect(self):
        """아두이노와 시리얼 연결"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 아두이노 초기화 대기
            self.is_connected = True
            print(f"아두이노 연결 성공: {self.port}")
            return True
        except Exception as e:
            print(f"아두이노 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """아두이노 연결 해제"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("아두이노 연결 해제")
    
    def send_command(self, command):
        """아두이노에 명령 전송"""
        if self.is_connected and self.serial_connection:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"아두이노에 명령 전송: {command}")
                return True
            except Exception as e:
                print(f"명령 전송 실패: {e}")
                return False
        return False
    
    def read_data(self):
        """아두이노에서 데이터 읽기"""
        if self.is_connected and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode().strip()
                    return data
            except Exception as e:
                print(f"데이터 읽기 실패: {e}")
        return None

# 아두이노 제어 함수들
def play_sound(arduino, sound_type):
    """
    아두이노를 통해 소리 재생
    sound_type: 'start', 'success', 'fail', 'complete', 'clap'
    """
    if arduino:
        arduino.send_command(f"SOUND:{sound_type}")

def play_voice_guide(arduino, message_type):
    """
    아두이노를 통해 음성 안내 재생
    message_type: 'welcome', 'exercise_start', 'follow_me', 'success', 'fail', 'complete'
    """
    if arduino:
        arduino.send_command(f"VOICE:{message_type}")

def control_led(arduino, led_state):
    """
    아두이노를 통해 LED 제어
    led_state: 'on', 'off', 'blink', 'green', 'red', 'blue'
    """
    if arduino:
        arduino.send_command(f"LED:{led_state}")

def play_random_mp3(arduino):
    """
    아두이노를 통해 랜덤 MP3 파일 재생
    MP3 파일: 0001, 0002, 0003, 0004 중 랜덤 선택
    """
    if arduino:
        mp3_number = random.randint(1, 4)
        mp3_file = f"{mp3_number:04d}"  # 0001, 0002, 0003, 0004 형태로 포맷
        arduino.send_command(f"MP3:{mp3_file}")
        print(f"MP3 재생: {mp3_file}")

def play_specific_mp3(arduino, mp3_file):
    """
    아두이노를 통해 특정 MP3 파일 재생
    mp3_file: 재생할 MP3 파일명 (예: "0001", "0002", "0003", "0004")
    """
    if arduino:
        arduino.send_command(f"MP3:{mp3_file}")
        print(f"MP3 재생: {mp3_file}")

# 전역 아두이노 객체
arduino_controller = None

def initialize_arduino(port='COM3'):
    """아두이노 초기화"""
    global arduino_controller
    arduino_controller = ArduinoController(port)
    if arduino_controller.connect():
        # 연결 성공시 LED 켜기
        control_led(arduino_controller, 'green')
        time.sleep(1)
        control_led(arduino_controller, 'off')
        return True
    return False

def cleanup_arduino():
    """아두이노 정리"""
    global arduino_controller
    if arduino_controller:
        arduino_controller.disconnect()

# 테스트 함수
def test_arduino_connection():
    """아두이노 연결 테스트"""
    if initialize_arduino():
        print("아두이노 연결 테스트 시작...")
        
        # LED 테스트
        control_led(arduino_controller, 'green')
        time.sleep(1)
        control_led(arduino_controller, 'off')
        
        # 소리 테스트
        play_sound(arduino_controller, 'start')
        time.sleep(2)
        
        # 음성 안내 테스트
        play_voice_guide(arduino_controller, 'welcome')
        time.sleep(3)
        
        cleanup_arduino()
        print("아두이노 연결 테스트 완료")
    else:
        print("아두이노 연결 실패")

if __name__ == "__main__":
    # 단독 실행시 테스트
    test_arduino_connection()
