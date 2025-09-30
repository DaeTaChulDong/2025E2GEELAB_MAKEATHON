import time
import threading
from ThreadManager import thread_manager, MessageType
from VideoProcessor import video_processing_thread
import SpeakerCommunication as ArduinoCommunication  # 아두이노 대신 스피커 사용

def safe_arduino_command(func, *args, **kwargs):
    """스피커 명령을 안전하게 실행 (논블로킹)"""
    def execute_command():
        try:
            if ArduinoCommunication.speaker_controller is not None and ArduinoCommunication.speaker_controller.is_connected:
                return func(*args, **kwargs)
            else:
                print(f"[EXERCISE] 스피커가 연결되지 않아 {func.__name__} 명령을 건너뜁니다.")
                return False
        except Exception as e:
            print(f"[EXERCISE] {func.__name__} 실행 중 오류: {e}")
            return False
    
    # 스피커 명령을 별도 스레드에서 논블로킹으로 실행
    speaker_thread = threading.Thread(target=execute_command, daemon=True)
    speaker_thread.start()
    return True

def run_exercise_mode():
    """멀티스레드 기반 운동 모드 실행"""
    print("[EXERCISE] 멀티스레드 운동 모드를 시작합니다...")
    
    # 스피커 시작 신호
    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')
    time.sleep(1)
    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'off')
    
    # 스레드 매니저 초기화
    global thread_manager
    thread_manager.shared_data.update({
        'current_stage': 'posture1',
        'video_completed': False,
        'exercise_running': True,
        'current_video_index': 0,
        'fail_count': 0
    })
    
    # 영상 처리 스레드 시작
    print("[EXERCISE] 영상 처리 스레드를 시작합니다...")
    if not thread_manager.start_video_thread(video_processing_thread):
        print("[EXERCISE] 영상 처리 스레드 시작 실패")
        return False
    
    # 메인 스레드에서 메시지 처리 및 아두이노 제어
    try:
        exercise_success = handle_exercise_messages()
        return exercise_success
    
    except KeyboardInterrupt:
        print("\n[EXERCISE] 사용자가 운동을 중단했습니다.")
        return False
    
    except Exception as e:
        print(f"[EXERCISE] 운동 모드 오류: {e}")
        return False
    
    finally:
        # 스레드 정리
        print("[EXERCISE] 스레드 정리 중...")
        thread_manager.shutdown()
        safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'off')

def handle_exercise_messages():
    """영상 처리 스레드로부터의 메시지를 처리하고 스피커를 제어"""
    stage_mp3_map = {
        'posture1': "0005",  # posture1 동작 안내
        'posture2': "0004",  # 왼손으로 골반 잡으세요
        'posture3': "0005"   # posture3 동작 안내
    }
    
    success_mp3_map = {
        'posture1': "0006",  # 성공 안내
        'posture2': "0006",  # 성공 안내
        'posture3': "0008"   # 모든 동작 완료 안내
    }
    
    fail_mp3_map = {
        'posture1': "0013",  # 팔을 더 펴달라는 안내
        'posture2': "0014",  # 실패 안내
        'posture3': "0011"   # posture3 첫 번째 실패 시 0011 재생
    }
    
    exercise_running = True
    current_stage = "posture1"
    
    print("[EXERCISE] 메시지 처리 루프 시작...")
    
    while exercise_running:
        # 영상 처리 스레드로부터 메시지 받기
        message = thread_manager.get_message_from_video(timeout=0.5)
        
        if message is None:
            # 메시지가 없으면 계속 대기
            continue
        
        print(f"[EXERCISE] 메시지 수신: {message.msg_type.value}")
        
        if message.msg_type == MessageType.POSE_DETECTED:
            # 사람 인식 성공
            print("[EXERCISE] 사람 인식 성공")
            safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.speaker_controller, 'green')
        
        elif message.msg_type == MessageType.POSE_LOST:
            # 사람 인식 실패
            print("[EXERCISE] 사람 인식 실패")
            # LED는 계속 켜둠 (깜빡거리지 않도록)
        
        elif message.msg_type == MessageType.POSTURE_SUCCESS:
            # 자세 성공
            stage = message.data.get('stage', current_stage)
            print(f"[EXERCISE] {stage} 자세 성공!")
            
            # 성공 안내 음성 재생
            if stage in success_mp3_map:
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, 
                                   ArduinoCommunication.speaker_controller, 
                                   success_mp3_map[stage])
            
            safe_arduino_command(ArduinoCommunication.control_led, 
                               ArduinoCommunication.speaker_controller, 'green')
            
            # 다음 단계로 전환
            if stage == "posture1":
                current_stage = "posture2"
                # posture2로 전환 시 상태 초기화
                thread_manager.send_to_video_thread(MessageType.NEXT_POSTURE)
            elif stage == "posture2":
                current_stage = "posture3"
                # posture3로 전환 시 상태 초기화
                thread_manager.send_to_video_thread(MessageType.NEXT_POSTURE)
            elif stage == "posture3":
                current_stage = "done"
                print("[EXERCISE] 모든 운동이 완료되었습니다!")
                exercise_running = False
                break
            
            # 공유 데이터 업데이트
            thread_manager.shared_data.set('current_stage', current_stage)
            
            # 다음 자세 안내
            if current_stage in stage_mp3_map:
                time.sleep(2)  # 2초 대기 후 다음 자세 안내
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, 
                                   ArduinoCommunication.speaker_controller, 
                                   stage_mp3_map[current_stage])
        
        elif message.msg_type == MessageType.POSTURE_FAIL:
            # 자세 실패
            stage = message.data.get('stage', current_stage)
            fail_count = message.data.get('fail_count', 0)
            print(f"[EXERCISE] {stage} 자세 실패 (실패 횟수: {fail_count})")
            
            # posture1과 posture2는 사람 인식만 되면 성공하므로 실패 메시지 재생하지 않음
            # posture3만 실패 메시지 재생
            if stage == "posture3" and stage in fail_mp3_map:
                safe_arduino_command(ArduinoCommunication.play_specific_mp3, 
                                   ArduinoCommunication.speaker_controller, 
                                   fail_mp3_map[stage])
            elif stage in ["posture1", "posture2"]:
                print(f"[EXERCISE] {stage}는 사람 인식 대기 중... (실패 메시지 재생 안함)")
        
        elif message.msg_type == MessageType.VIDEO_END:
            # 영상 종료
            completed = message.data.get('completed', False)
            stage = message.data.get('stage', current_stage)
            
            if completed:
                print(f"[EXERCISE] {stage} 영상 완료")
                # 영상 처리 스레드가 자동으로 다음 영상으로 전환
            else:
                print(f"[EXERCISE] {stage} 영상 미완료로 재시도")
                # 영상 처리 스레드가 자동으로 재시도
        
        elif message.msg_type == MessageType.CAMERA_ERROR:
            # 카메라 오류
            print("[EXERCISE] 카메라 오류 발생")
            safe_arduino_command(ArduinoCommunication.play_random_mp3, 
                               ArduinoCommunication.speaker_controller)
            exercise_running = False
            return False
        
        elif message.msg_type == MessageType.SHUTDOWN:
            # 종료 요청
            print("[EXERCISE] 종료 요청 수신")
            exercise_running = False
            break
        
        # 운동 상태 확인
        if not thread_manager.shared_data.get('exercise_running'):
            print("[EXERCISE] 운동이 중단되었습니다.")
            exercise_running = False
            break
    
    print("[EXERCISE] 메시지 처리 루프 종료")
    return current_stage == "done"  # 모든 자세를 완료했으면 True 반환