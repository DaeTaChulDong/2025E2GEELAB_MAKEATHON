import time
import cv2
import mediapipe as mp
import numpy as np
# ReferenceVideo import 제거 - 이제 동작별로 다른 영상 파일을 직접 사용
from ArduinoCommunication import arduino_controller, play_voice_guide, play_sound, control_led, play_random_mp3, play_specific_mp3

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

def give_feedback(angle, target_angle, tolerance=30):  # 각도 비교 피드백
    diff = abs(angle - target_angle)
    if diff <= tolerance:
        return "정답! 축하합니다! 박수! 👏", True
    else:
        # 오차에 따른 메시지
        if diff <= 30:
            return "조금만 더 팔을 펴볼까요?", False
        else:
            return "오답! 다시 해보세요!", False

def change_reference_video(ref, new_stage, video_paths):
    """동작 단계에 따라 따라하기 영상 변경"""
    new_video_path = video_paths[new_stage]
    ref.release()  # 기존 영상 해제
    new_ref = cv2.VideoCapture(new_video_path)
    if new_ref.isOpened():
        return new_ref
    else:
        print(f"영상 파일을 열 수 없습니다: {new_video_path}")
        return ref

def run_exercise_mode():
    play_random_mp3(arduino_controller)  # 운동 모드 시작 안내
    control_led(arduino_controller, 'blue')  # 운동 모드 시작 LED
    time.sleep(1)
    control_led(arduino_controller, 'off')
    
    cap = cv2.VideoCapture(0)  # 웹캠 열기 (왼쪽)
    
    if not cap.isOpened():
        play_random_mp3(arduino_controller)  # 카메라 오류 안내
        control_led(arduino_controller, 'red')
        return
    
    # 동작별 영상 파일 경로
    video_paths = {
        "raise": "자세1 동영상 파일 경로",    # 첫 번째 자세
        "hands_on_waist": "자세2 동영상 파일 경로"  # 두 번째 자세
    }
    
    # 현재 동작에 맞는 영상 열기
    current_video_path = video_paths["raise"]
    ref = cv2.VideoCapture(current_video_path)
    
    if not ref.isOpened():
        play_random_mp3(arduino_controller)  # 영상 오류 안내
        control_led(arduino_controller, 'red')
        return
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        stage = "raise"   # 동작 단계
        detected = False
        fail_count = 0
        last_check_time = 0
        check_interval = 3  # 3초마다 체크

        while True:
            # 웹캠 프레임 읽기 (왼쪽)
            ret1, frame1 = cap.read()
            # 따라하기 영상 프레임 읽기 (오른쪽)
            ret2, frame2 = ref.read()

            if not ret1:
                play_random_mp3(arduino_controller)  # 웹캠 오류 안내
                control_led(arduino_controller, 'red')
                break
            if not ret2:
                # 영상이 끝나면 처음부터 다시 재생
                ref.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret2, frame2 = ref.read()
                if not ret2:
                    play_random_mp3(arduino_controller)  # 영상 오류 안내
                    control_led(arduino_controller, 'red')
                    break

            # 두 영상을 같은 크기로 맞추기 (640x480)
            frame1 = cv2.resize(frame1, (640, 480))
            frame2 = cv2.resize(frame2, (640, 480))
            
            # 좌우로 합치기 (왼쪽: 웹캠, 오른쪽: 따라하기 영상)
            combined = cv2.hconcat([frame1, frame2])

            # Mediapipe Pose 처리 (카메라 영상만 분석)
            image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # 사람 인식 확인
            if results.pose_landmarks:
                if not detected:
                    play_random_mp3(arduino_controller)  # 인식 성공 안내
                    control_led(arduino_controller, 'green')
                    detected = True
            else:
                if detected:  # 이전에 인식되었던 경우에만 메시지 출력
                    play_random_mp3(arduino_controller)  # 인식 실패 안내
                    control_led(arduino_controller, 'red')

            # 3초마다 자세 판정
            current_time = time.time()
            if detected and current_time - last_check_time >= check_interval:
                play_random_mp3(arduino_controller)  # 자세 분석 시작 안내
                last_check_time = current_time
                
                try:
                    landmarks = results.pose_landmarks.landmark

                    # 좌측 팔 어깨-팔꿈치-손목 좌표
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    # 팔 각도 계산
                    angle = calculate_angle(shoulder, elbow, wrist)

                    # 만세 동작: 팔 각도가 펴지고(>160도), 손목이 어깨보다 위쪽(y 값이 작을 때)
                    if stage == "raise":
                        play_random_mp3(arduino_controller)  # 만세 동작 시범 안내
                        play_voice_guide(arduino_controller, 'follow_me')
                        
                        play_random_mp3(arduino_controller)  # 따라하기 안내
                        if angle > 160 and wrist[1] < shoulder[1]:
                            play_random_mp3(arduino_controller)  # 성공 안내
                            play_voice_guide(arduino_controller, 'success')
                            play_sound(arduino_controller, 'success')
                            control_led(arduino_controller, 'green')
                            stage = "hands_on_waist"
                            # 두 번째 동작 영상으로 변경
                            ref = change_reference_video(ref, stage, video_paths)
                            fail_count = 0
                            time.sleep(2)
                        else:
                            fail_count += 1
                            play_random_mp3(arduino_controller)  # 실패 안내
                            play_voice_guide(arduino_controller, 'fail')
                            play_sound(arduino_controller, 'fail')
                            control_led(arduino_controller, 'red')
                            if fail_count >= 3:
                                play_random_mp3(arduino_controller)  # 다음 동작 안내
                                stage = "hands_on_waist"
                                # 두 번째 동작 영상으로 변경
                                ref = change_reference_video(ref, stage, video_paths)
                                fail_count = 0
                                time.sleep(2)

                    # 허리에 손 얹기 동작: 팔과 허리가 일직선에 가까운지 각도로 판정
                    elif stage == "hands_on_waist":
                        play_random_mp3(arduino_controller)  # 허리 동작 안내
                        play_voice_guide(arduino_controller, 'follow_me')
                        play_reference_video(ref, 91, 180, (640, 480))
                        
                        play_random_mp3(arduino_controller)  # 따라하기 안내
                        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        
                        # 팔꿈치-어깨-허리 각도 계산 (팔과 허리가 일직선에 가까운지 확인)
                        waist_angle = calculate_angle(elbow, shoulder, hip)
                        
                        if waist_angle > 160:  # 팔과 허리가 일직선에 가까우면 성공
                            play_random_mp3(arduino_controller)  # 성공 안내
                            play_voice_guide(arduino_controller, 'success')
                            play_sound(arduino_controller, 'success')
                            control_led(arduino_controller, 'green')
                            stage = "done"
                            fail_count = 0
                            time.sleep(3)
                        elif waist_angle < 150:  # 각도가 150도 미만이면 0001.mp3 재생
                            play_specific_mp3(arduino_controller, "0001")  # 0001.mp3 재생
                            play_voice_guide(arduino_controller, 'fail')
                            play_sound(arduino_controller, 'fail')
                            control_led(arduino_controller, 'red')
                        else:  # 150도 이상 160도 미만
                            fail_count += 1
                            play_random_mp3(arduino_controller)  # 실패 안내
                            play_voice_guide(arduino_controller, 'fail')
                            play_sound(arduino_controller, 'fail')
                            control_led(arduino_controller, 'red')
                            if fail_count >= 3:
                                play_random_mp3(arduino_controller)  # 완료 안내
                                stage = "done"
                                fail_count = 0
                                time.sleep(2)
                    
                    if stage == "done":
                        play_random_mp3(arduino_controller)  # 모든 동작 완료 안내
                        control_led(arduino_controller, 'green')
                        break

                except Exception as e:
                    play_random_mp3(arduino_controller)  # 오류 안내
                    control_led(arduino_controller, 'red')
                    pass
            
            # 관절 그리기 (웹캠 영상에만)
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame1, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # 화면 출력 (좌: 웹캠 + 관절, 우: 따라하기 영상)
            cv2.imshow("운동 모드 (왼쪽=웹캠/오른쪽=따라하기영상)", combined)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                play_random_mp3(arduino_controller)  # 종료 안내
                control_led(arduino_controller, 'red')
                break
    
    cap.release()
    ref.release()
    cv2.destroyAllWindows()
    play_random_mp3(arduino_controller)  # 운동 모드 종료 안내

    control_led(arduino_controller, 'off')
