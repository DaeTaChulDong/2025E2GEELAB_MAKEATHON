try:
    import serial  # type: ignore
except ImportError:
    print("pyserial 모듈이 설치되지 않았습니다. 'pip install pyserial' 명령으로 설치해주세요.")
    serial = None
import time
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
            print(f"[ARDUINO] COM3 포트에 연결을 시도합니다...")
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 아두이노 초기화 대기
            self.is_connected = True
            print(f"[ARDUINO] 아두이노 연결 성공: {self.port}")
            return True
        except Exception as e:
            print(f"[ARDUINO] 아두이노 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """아두이노 연결 해제"""
        print("[ARDUINO] 아두이노 연결을 해제합니다...")
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("[ARDUINO] 아두이노 연결 해제 완료")
    
    def send_command(self, command):
        """아두이노에 명령 전송 (직접 전송)"""
        if self.is_connected and self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                return True
            except Exception as e:
                self.is_connected = False
                return False
        else:
            return False
    
    def read_data(self):
        """아두이노에서 데이터 읽기 (기존 메서드 - 호환성 유지)"""
        if self.is_connected and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode().strip()
                    return data
            except Exception as e:
                pass
        return None

# 전역 아두이노 객체
arduino_controller = None

def initialize_arduino(port='COM3'):
    """아두이노 초기화"""
    global arduino_controller
    print(f"[ARDUINO] 아두이노 초기화 시작 (포트: {port})")
    
    # 기존 연결이 있으면 정리
    if arduino_controller:
        print("[ARDUINO] 기존 연결을 정리합니다...")
        arduino_controller.disconnect()
        time.sleep(1)
    
    arduino_controller = ArduinoController(port)
    if arduino_controller.connect():
        print("[ARDUINO] 아두이노 초기화 완료")
        print(f"[ARDUINO] arduino_controller 객체 생성됨: {arduino_controller}")
        print(f"[ARDUINO] 연결 상태: {arduino_controller.is_connected}")
        return True
    else:
        print("[ARDUINO] 아두이노 초기화 실패")
        arduino_controller = None
        return False

def cleanup_arduino():
    """아두이노 정리"""
    global arduino_controller
    if arduino_controller:
        print("[ARDUINO] 아두이노 정리 시작...")
        arduino_controller.disconnect()
        arduino_controller = None
        print("[ARDUINO] 아두이노 정리 완료")

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
    아두이노를 통해 LED 제어 (5번 핀, 녹색 LED만)
    led_state: 'green', 'off'
    """
    if arduino:
        # 5번 핀에 연결된 녹색 LED만 지원
        if led_state == 'green':
            arduino.send_command("LED:green")
        elif led_state == 'off':
            arduino.send_command("LED:off")

def play_random_mp3(arduino):
    """
    아두이노를 통해 랜덤 MP3 파일 재생
    MP3 파일: 0001, 0002, 0003, 0004 중 랜덤 선택
    """
    if arduino:
        mp3_number = random.randint(1, 4)
        mp3_file = f"{mp3_number:04d}"  # 0001, 0002, 0003, 0004 형태로 포맷
        arduino.send_command(f"MP3:{mp3_file}")

def play_specific_mp3(arduino, mp3_file):
    """
    아두이노를 통해 특정 MP3 파일 재생
    mp3_file: 재생할 MP3 파일명 (예: "0001", "0002", "0003", "0004")
    """
    if arduino:
        arduino.send_command(f"MP3:{mp3_file}")
        # MP3 재생 완료까지 5초 대기
        time.sleep(5)

# 테스트 함수
def test_arduino_connection():
    """아두이노 연결 테스트"""
    if initialize_arduino():
        print("아두이노 연결 테스트 시작...")
        
        # LED 테스트
        control_led(arduino_controller, 'green')
        time.sleep(2)
        control_led(arduino_controller, 'off')
        
        # MP3 테스트
        play_specific_mp3(arduino_controller, "0001")
        
        cleanup_arduino()
        print("아두이노 연결 테스트 완료")
    else:
        print("아두이노 연결 실패")

if __name__ == "__main__":
    # 단독 실행시 테스트
    print("아두이노 통신 테스트 시작")
    test_arduino_connection()