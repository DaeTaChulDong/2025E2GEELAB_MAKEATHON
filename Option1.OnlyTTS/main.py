from SpeechRecognition import listen_command, listen_background
import sys
import time
from ExerciseMode import run_exercise_mode

def main():
    print("프로그램 시작. '운동하자'라고 말하면 시작합니다.")
    
    # 백그라운드에서 종료 명령 감지
    listen_background()
    
    while True:
        command = listen_command()
        if command == "운동하자":
            print("운동을 시작합니다.")
            run_exercise_mode()  # 실행 모드 함수 호출
            
            # 운동 완료 후 메시지
            print("모든 운동이 끝났습니다. 수고하셨습니다.")
            print("다음에 또 만나요!")
            
            # 선택 1: 프로그램 종료
            sys.exit()
            
            # 선택 2: 다시 대기 모드로 복귀 (원하면 위 sys.exit() 대신 아래 주석 해제)
            # print("다시 '운동하자'라고 말하면 운동을 시작할 수 있습니다.")
            # continue
            
        elif command == "종료":
            print("프로그램을 종료합니다.")
            sys.exit()
        
        time.sleep(1)  # CPU 사용량 줄이기

if __name__ == "__main__":
    main()