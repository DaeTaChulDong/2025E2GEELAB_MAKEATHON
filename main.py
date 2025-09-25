from SpeechRecognition import listen_command, listen_background, stop_listening
import sys
import time
from ExerciseMode import run_exercise_mode
from ArduinoCommunication import initialize_arduino, cleanup_arduino, play_voice_guide, play_sound, control_led, play_random_mp3, arduino_controller

def main():
    play_random_mp3(arduino_controller)  # 프로그램 시작 안내
    control_led(arduino_controller, 'blue')
    
    # 아두이노 초기화
    play_random_mp3(arduino_controller)  # 아두이노 연결 시도 안내
    if initialize_arduino('COM3'):  # 포트는 환경에 맞게 수정
        play_random_mp3(arduino_controller)  # 연결 성공 안내
        control_led(arduino_controller, 'green')  # 연결 성공 LED
    else:
        play_random_mp3(arduino_controller)  # 연결 실패 안내
        control_led(arduino_controller, 'red')
    
    # 배경 음성 인식 스레드 시작
    listen_background()
    
    while True:
        command = listen_command()
        if command == "운동하자":
            play_random_mp3(arduino_controller)  # 운동 시작 안내
            control_led(arduino_controller, 'blue')
            
            # 아두이노를 통한 음성 안내
            play_voice_guide(arduino_controller, 'welcome')
            play_sound(arduino_controller, 'start')
            control_led(arduino_controller, 'blue')
            
            run_exercise_mode()  # 실행 모드 함수 호출
            
            # 운동 완료 후 처리
            play_random_mp3(arduino_controller)  # 운동 완료 안내
            control_led(arduino_controller, 'green')
            
            # 아두이노를 통한 완료 안내
            play_voice_guide(arduino_controller, 'complete')
            play_sound(arduino_controller, 'clap')
            control_led(arduino_controller, 'green')
            
            play_random_mp3(arduino_controller)  # 다음에 또 만나요 안내
            
            # 사용자 선택: 종료 또는 대기 모드로 복귀
            choice = input("프로그램을 종료하시겠습니까? (y/n): ").lower()
            if choice == 'y':
                play_random_mp3(arduino_controller)  # 프로그램 종료 안내
                cleanup_arduino()
                sys.exit()
            else:
                play_random_mp3(arduino_controller)  # 대기 모드 안내
                control_led(arduino_controller, 'off')
                continue
                
        elif command == "종료":
            play_random_mp3(arduino_controller)  # 운동 종료 안내
            play_voice_guide(arduino_controller, 'goodbye')
            control_led(arduino_controller, 'red')
            stop_listening()
            cleanup_arduino()
            sys.exit()
        elif command is None:
            continue  # 인식 실패시 다시 시도

if __name__ == "__main__":
    main()