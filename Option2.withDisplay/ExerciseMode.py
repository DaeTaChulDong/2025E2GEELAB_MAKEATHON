import time
import cv2
import mediapipe as mp
import numpy as np
# ReferenceVideo import 제거 - 이제 동작별로 다른 영상 파일을 직접 사용
import ArduinoCommunication

def safe_arduino_command(func, *args, **kwargs):
    """아두이노 명령을 안전하게 실행"""
    try:
        if ArduinoCommunication.arduino_controller is not None and ArduinoCommunication.arduino_controller.is_connected:
            return func(*args, **kwargs)
        else:
            print(f"[EXERCISE] 아두이노가 연결되지 않아 {func.__name__} 명령을 건너뜁니다.")
            print(f"[EXERCISE] arduino_controller: {ArduinoCommunication.arduino_controller}")
            if ArduinoCommunication.arduino_controller is not None:
                print(f"[EXERCISE] is_connected: {ArduinoCommunication.arduino_controller.is_connected}")
            return False
    except Exception as e:
        print(f"[EXERCISE] {func.__name__} 실행 중 오류: {e}")
        return False

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(x, y, z):  # 세점사이 각도계산
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    
    yx = x - y
    yz = z - y
    
    cosine_angle = np.dot(yx, yz) / (np.linalg.norm(yx) * np.linalg.norm(yz))
    angle = np.arccos(cosine_angle)
    return int(np.degrees(angle))

def change_to_next_video(ref, video_paths, current_index):
    """다음 영상으로 순차 전환"""
    ref.release()  # 기존 영상 해제
    
    # 다음 영상 인덱스 계산 (순환)
    next_index = (current_index + 1) % len(video_paths)
    new_video_path = video_paths[next_index]
    
    new_ref = cv2.VideoCapture(new_video_path)
    if new_ref.isOpened():
        print(f"다음 영상으로 전환: {new_video_path}")
        return new_ref, next_index
    else:
        print(f"영상 파일을 열 수 없습니다: {new_video_path}")
        # 실패시 원래 영상으로 복구
        fallback_ref = cv2.VideoCapture(video_paths[current_index])
        return fallback_ref, current_index

def run_exercise_mode():
    print("운동 모드를 시작합니다...")
    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.arduino_controller, 'green')  # 운동 모드 시작 LED
    time.sleep(1)
    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.arduino_controller, 'off')
    
    # 카메라 연결 (0번 카메라 직접 연결)
    print("카메라 0번에 연결 중...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("카메라 0번을 열 수 없습니다. 운동 모드를 종료합니다.")
        safe_arduino_command(ArduinoCommunication.play_random_mp3, ArduinoCommunication.arduino_controller)  # 카메라 오류 안내
        return False  # 운동 모드 실패
    else:
        print("카메라 0번 연결 성공!")
    
    # 동작별 영상 파일 경로 (순차 재생용)
    video_paths = [
        r"C:\Users\PC2403\Desktop\posture1.mp4",    # 첫 번째 자세
        r"C:\Users\PC2403\Desktop\posture2.mp4",   # 두 번째 자세
        r"C:\Users\PC2403\Desktop\posture3.mp4"       # 세 번째 자세
    ]
    
    # 첫 번째 영상 열기
    current_video_index = 0
    print(f"영상 파일 열기 시도: {video_paths[current_video_index]}")
    ref = cv2.VideoCapture(video_paths[current_video_index])
    
    if not ref.isOpened():
        print(f"영상 파일을 열 수 없습니다: {video_paths[current_video_index]}")
        print("파일이 존재하는지 확인해주세요.")
        cap.release()  # 카메라 해제
        return False  # 운동 모드 실패
    else:
        print(f"영상 파일 열기 성공: {video_paths[current_video_index]}")
    
    print("MediaPipe Pose 초기화 중...")
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        print("MediaPipe Pose 초기화 완료!")
        stage = "posture1"   # 동작 단계
        detected = False
        fail_count = 0
        last_check_time = 0
        last_fail_time = 0  # 마지막 인식 실패 시간
        check_interval = 10  # 10초마다 체크
        fail_interval = 5    # 5초마다 인식 실패 메시지
        
        # 영상 재생 제어 변수
        video_retry_count = 0  # 영상 재시도 횟수
        max_retry_count = 3    # 최대 재시도 횟수
        video_completed = False  # 자세 완료 여부

        print("운동 모드 메인 루프 시작!")
        print("ESC 키 또는 'q' 키를 누르면 운동 모드를 종료할 수 있습니다.")
        frame_count = 0
        while True:
            # 웹캠 프레임 읽기 (왼쪽)
            ret1, frame1 = cap.read()
            # 따라하기 영상 프레임 읽기 (오른쪽)
            ret2, frame2 = ref.read()
            
            frame_count += 1
            if frame_count % 100 == 0:  # 100프레임마다 상태 출력
                print(f"프레임 {frame_count}: 웹캠={ret1}, 참조영상={ret2}")

            if not ret1:
                print("웹캠 프레임 읽기 실패!")
                safe_arduino_command(ArduinoCommunication.play_random_mp3, ArduinoCommunication.arduino_controller)  # 웹캠 오류 안내
                break
            if not ret2:
                # 영상이 끝났을 때의 처리
                if video_completed:
                    # 자세가 완료되었으면 다음 영상으로 전환
                    print("자세 완료! 다음 영상으로 전환합니다.")
                    ref, current_video_index = change_to_next_video(ref, video_paths, current_video_index)
                    video_retry_count = 0  # 재시도 횟수 초기화
                    video_completed = False  # 완료 상태 초기화
                else:
                    # 자세가 완료되지 않았으면 재시도
                    if video_retry_count < max_retry_count:
                        video_retry_count += 1
                        print(f"자세 미완료. 영상을 다시 재생합니다. ({video_retry_count}/{max_retry_count})")
                        time.sleep(3)  # 3초 대기
                        ref.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 영상 처음으로 되돌리기
                    else:
                        # 최대 재시도 횟수 초과 시 다음 영상으로 전환
                        print("최대 재시도 횟수 초과. 다음 영상으로 전환합니다.")
                        ref, current_video_index = change_to_next_video(ref, video_paths, current_video_index)
                        video_retry_count = 0  # 재시도 횟수 초기화
                
                ret2, frame2 = ref.read()
                if not ret2:
                    break

            # 두 영상을 같은 크기로 맞추기 (640x480)
            frame1 = cv2.resize(frame1, (640, 480))
            frame2 = cv2.resize(frame2, (640, 480))

            # Mediapipe Pose 처리 (카메라 영상만 분석)
            image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # MediaPipe 결과를 frame1에 반영
            frame1 = image.copy()

            # 사람 인식 확인
            if results.pose_landmarks:
                if not detected:
                    print("인식 성공")  # 인식 성공 안내
                    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.arduino_controller, 'green')
                    detected = True
            else:
                if detected:  # 이전에 인식되었던 경우에만 메시지 출력
                    current_time = time.time()
                    if current_time - last_fail_time >= fail_interval:  # 5초마다만 인식 실패 메시지 출력
                        print("인식 실패") # 인식 실패 안내
                        last_fail_time = current_time

            # 10초마다 자세 판정
            current_time = time.time()
            if detected and current_time - last_check_time >= check_interval: # 자세 분석 시작 안내
                last_check_time = current_time
                
                try:
                    landmarks = results.pose_landmarks.landmark

                    # posture1 동작: 의자에 앉아서 상체 스트레칭 (오른팔 위로 뻗고 왼손으로 오른팔 잡기)
                    if stage == "posture1":
                        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller,"0005")  # posture1 동작 시범 안내
                        
                        # 상체 노드들만 사용 (하체 제외)
                        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                        right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                       landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        
                        # 오른팔 각도 계산 (어깨-팔꿈치-손목)
                        right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                        
                        # 왼팔 각도 계산 (어깨-팔꿈치-손목)
                        left_arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
                        
                        # posture1 판단 기준:
                        # 1. 오른팔이 위로 뻗어져 있음 (각도 > 160도, 손목이 어깨보다 위)
                        # 2. 왼팔이 구부러져 있음 (각도 < 120도)
                        # 3. 왼손이 오른팔 근처에 있음 (거리 체크)
                        right_arm_extended = right_arm_angle > 160 and right_wrist[1] < right_shoulder[1]
                        left_arm_bent = left_arm_angle < 120
                        
                        # 왼손과 오른팔의 거리 계산
                        left_hand_to_right_arm_distance = np.sqrt((left_wrist[0] - right_elbow[0])**2 + (left_wrist[1] - right_elbow[1])**2)
                        hands_close = left_hand_to_right_arm_distance < 0.15  # 임계값 조정 가능
                        
                        if right_arm_extended and left_arm_bent and hands_close:
                            safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller,"0008")  # 성공 안내
                            safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.arduino_controller, 'green')
                            video_completed = True  # 자세 완료 플래그 설정
                            stage = "posture2"
                            fail_count = 0
                        else:  # 팔을 덜 편 경우
                            fail_count += 1
                            safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0013")  # 팔을 더 펴달라는 안내
                            # 실패 시에는 영상이 끝날 때까지 기다린 후 재시도 로직 적용


                    # posture2 동작: 의자에 앉아서 왼손으로 오른쪽 골반(허리) 잡기
                    elif stage == "posture2":
                        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0004")  # 왼손으로골반잡으세요
                        
                        # 상체 노드들 정의 (하체 제외)
                        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                        
                        # 왼손과 오른쪽 골반의 거리 계산
                        left_hand_to_right_hip_distance = np.sqrt((left_wrist[0] - right_hip[0])**2 + (left_wrist[1] - right_hip[1])**2)
                        
                        # posture2 판단 기준:
                        # 1. 왼손이 오른쪽 골반 근처에 있음 (거리 체크)
                        # 2. 왼손이 오른쪽 골반보다 아래쪽에 있음 (y 좌표 체크)
                        hand_near_hip = left_hand_to_right_hip_distance < 0.12  # 임계값 조정 가능
                        hand_below_hip = left_wrist[1] > right_hip[1]  # 왼손이 오른쪽 골반보다 아래
                        
                        if hand_near_hip and hand_below_hip:
                            safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0006")  # 성공 안내
                            video_completed = True  # 자세 완료 플래그 설정
                            stage = "posture3"
                            fail_count = 0
                        else:
                            fail_count += 1
                            safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0014")  # 실패 안내
                            # 실패 시에는 영상이 끝날 때까지 기다린 후 재시도 로직 적용

                    # posture3 동작: 의자에 앉아서 오른쪽으로 기울이면서 오른팔 위로 뻗고 왼손을 오른쪽 골반에 대기
                    elif stage == "posture3":
                        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0005")  # posture3 동작 안내
                        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0006")
                        
                        # 상체 노드들 정의 (하체 제외)
                        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                       landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                        right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                        
                        # 오른팔 각도 계산 (어깨-팔꿈치-손목)
                        right_arm_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
                        
                        # 왼손과 오른쪽 골반의 거리 계산
                        left_hand_to_right_hip_distance = np.sqrt((left_wrist[0] - right_hip[0])**2 + (left_wrist[1] - right_hip[1])**2)
                        
                        # posture3 판단 기준:
                        # 1. 오른팔이 위로 뻗어져 있음 (각도 > 160도, 손목이 어깨보다 위)
                        # 2. 왼손이 오른쪽 골반 근처에 있음 (거리 체크)
                        # 3. 왼손이 오른쪽 골반보다 아래쪽에 있음 (y 좌표 체크)
                        right_arm_extended = right_arm_angle > 100 and right_wrist[1] < right_shoulder[1]
                        hand_near_hip = left_hand_to_right_hip_distance < 0.12  # 임계값 조정 가능
                        hand_below_hip = left_wrist[1] > right_hip[1]  # 왼손이 오른쪽 골반보다 아래
                        
                        if right_arm_extended and hand_near_hip and hand_below_hip:
                            video_completed = True  # 자세 완료 플래그 설정
                            stage = "done"
                            fail_count = 0
                        else:
                            fail_count += 1
                            safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0015")  # 실패 안내
                            safe_arduino_command(ArduinoCommunication.play_voice_guide, ArduinoCommunication.arduino_controller, 'fail')
                            safe_arduino_command(ArduinoCommunication.play_sound, ArduinoCommunication.arduino_controller, 'fail')
                            # 실패 시에는 영상이 끝날 때까지 기다린 후 재시도 로직 적용
                    
                    if stage == "done":
                        safe_arduino_command(ArduinoCommunication.play_specific_mp3, ArduinoCommunication.arduino_controller, "0007")  # 모든 동작 완료 안내
                        break

                except Exception as e:
                    pass
            
            # 관절 그리기 (웹캠 영상에만) - 파란색 연결선
            if results.pose_landmarks:
                # 관절점은 빨간색, 연결선은 파란색으로 설정
                mp_drawing.draw_landmarks(
                    frame1, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),  # 관절점: 빨간색
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)  # 연결선: 파란색
                )
            
            # MediaPipe 처리 후 combined 영상 생성
            combined = cv2.hconcat([frame1, frame2])
            
            # 화면 출력 (좌: 웹캠 + 관절, 우: 따라하기 영상)
            cv2.imshow("운동 모드 (왼쪽=웹캠/오른쪽=따라하기영상)", combined)

            # ESC 키(27) 또는 'q' 키로 종료
            key = cv2.waitKey(10) & 0xFF
            if key == 27 or key == ord('q'):  # ESC 키 또는 'q' 키
                print("ESC 키를 눌러 운동 모드를 종료합니다.")
                break
    
    cap.release()
    ref.release()
    cv2.destroyAllWindows()

    safe_arduino_command(ArduinoCommunication.control_led, ArduinoCommunication.arduino_controller, 'off')
    return True  # 운동 모드 성공적으로 완료
