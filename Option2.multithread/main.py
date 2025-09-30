from SpeechRecognition import listen_command_direct
import sys
import time
from ExerciseMode import run_exercise_mode
import SpeakerCommunication as ArduinoCommunication  # 아두이노 대신 스피커 사용
from ThreadManager import thread_manager

def safe_speaker_command(func, *args, **kwargs):
    """스피커 명령을 안전하게 실행"""
    try:
        if ArduinoCommunication.speaker_controller is not None and ArduinoCommunication.speaker_controller.is_connected:
            print(f"[MAIN] 스피커 명령 실행: {func.__name__}")
            return func(*args, **kwargs)
        else:
            print(f"[MAIN] 스피커가 연결되지 않아 {func.__name__} 명령을 건너뜁니다.")
            print(f"[MAIN] speaker_controller: {ArduinoCommunication.speaker_controller}")
            if ArduinoCommunication.speaker_controller is not None:
                print(f"[MAIN] is_connected: {ArduinoCommunication.speaker_controller.is_connected}")
            return False
    except Exception as e:
        print(f"[MAIN] {func.__name__} 실행 중 오류: {e}")
        return False

# 호환성을 위한 별칭
safe_arduino_command = safe_speaker_command

def main():
    print("[MAIN] 프로그램을 시작합니다...")
    
    # 1단계: 스피커 초기화 (음성 인식 전에 먼저 연결)
    print("[MAIN] 1단계: 내장 스피커를 초기화합니다...")
    if ArduinoCommunication.initialize_speaker():
        print("[MAIN] 스피커 초기화 성공")
        safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')  # 연결 성공 안내
        time.sleep(1)  # 1초 대기
        safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'off')  # 완료 안내
        
        # 프로그램 정상 실행 확인
        print("[MAIN] 프로그램이 정상적으로 실행되었습니다.")
        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0001")
        time.sleep(3)  # 3초간 대기
    else:
        print("[MAIN] 스피커 초기화 실패")
        print("[MAIN] 스피커 없이 프로그램을 계속 실행합니다.")
    
    # 2단계: 스피커 연결 상태 재확인
    print("[MAIN] 2단계: 스피커 연결 상태를 재확인합니다...")
    if ArduinoCommunication.speaker_controller is not None:
        print(f"[MAIN] 스피커 연결 상태: {ArduinoCommunication.speaker_controller.is_connected}")
    else:
        print("[MAIN] 스피커 컨트롤러가 None입니다.")
    
    print("[MAIN] 음성 명령을 기다리고 있습니다... ('운동하자' 또는 '종료')")
    
    try:
        while True:
            # 음성 명령어 직접 인식 (블로킹)
            command = listen_command_direct()
            
            if command == "운동하자":
                print("[MAIN] 운동하자 명령을 받았습니다!")
                
                # 스피커 상태 재확인
                print(f"[MAIN] 스피커 상태 확인: controller={ArduinoCommunication.speaker_controller is not None}")
                if ArduinoCommunication.speaker_controller is not None:
                    print(f"[MAIN] 연결 상태: {ArduinoCommunication.speaker_controller.is_connected}")
                
                # 스피커 명령들을 안전하게 실행
                print("[MAIN] 음성 안내를 시작합니다...")
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0001")
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0002")  # 오늘도 재밌게 운동해 볼까요?
                safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')
                
                # 스피커를 통한 음성 안내
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0003")   # 좋아요함께즐겁게운동해봐요
                safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')
                
                # 운동 모드 실행
                print("[MAIN] 운동 모드를 시작합니다...")
                exercise_success = run_exercise_mode()  # 실행 모드 함수 호출
                
                # 운동 모드 결과에 따른 처리
                if exercise_success:
                    # 운동 모드 성공적으로 완료
                    print("[MAIN] 운동이 완료되었습니다!")
                    
                    safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0008")  # 오늘은여기까지또만나요
                    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')
                    safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.speaker_controller, "0009")  # 오늘하루더맑아질거예요요
                    
                    # 사용자 선택: 종료 또는 대기 모드로 복귀
                    choice = input("[MAIN] 프로그램을 종료하시겠습니까? (y/n): ").lower()
                    if choice == 'y':
                        break
                    else:
                        safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'off')
                        time.sleep(2)  # 2초 대기 후 다시 명령 대기
                        continue
                else:
                    # 운동 모드 실패 (카메라나 영상 파일 문제)
                    print("[MAIN] 운동 모드를 시작할 수 없습니다. 다시 시도해주세요.")
                    time.sleep(2)  # 2초 대기 후 다시 명령 대기
                    continue
                    
            elif command == "종료":
                print("[MAIN] 종료 명령을 받았습니다!")
                break
            elif command is None:
                # 음성 인식 실패 또는 타임아웃 - 다시 시도
                continue
            else:
                print(f"[MAIN] 알 수 없는 명령: {command}")
                print("[MAIN] '운동하자' 또는 '종료'라고 말해주세요.")
                continue
                
    except KeyboardInterrupt:
        print("\n[MAIN] 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"[MAIN] 오류 발생: {e}")
    finally:
        # 정리 작업
        print("[MAIN] 프로그램을 종료합니다...")
        
        # 스레드 매니저 정리
        try:
            thread_manager.shutdown()
            print("[MAIN] 스레드 정리 완료")
        except Exception as e:
            print(f"[MAIN] 스레드 정리 중 오류: {e}")
        
        # 스피커 정리
        ArduinoCommunication.cleanup_speaker()
        print("[MAIN] 프로그램 종료 완료")

if __name__ == "__main__":
    main()
