import time
import cv2
import mediapipe as mp
import numpy as np
from TTS import speak, speak_async

mp_drawing=mp.solutions.drawing_utils
mp_pose=mp.solutions.pose

def calculate_angle(x,y,z): #세점사이 각도계산
    x=np.array(x)
    y=np.array(y)
    z=np.array(z)
    
    yx=x-y
    yz=z-y
    
    cosine_angle=np.dot(yx,yz)/(np.linalg.norm(yx)*np.linalg.norm(yz))
    angle=np.arccos(cosine_angle)
    return int(np.degrees(angle))

def give_feedback(angle, target_angle, tolerance=30): #각도 비교 피드백
    diff = abs(angle - target_angle)
    if diff <= tolerance:
        return "정답! 축하합니다", True
    else:
        #오차에 따른 메시지
        if diff <= 30:
            return "조금만 더 팔을 펴볼까요?", False
        else:
            return "오답! 다시 해보세요!", False

def run_exercise_mode():
    print("운동 모드를 시작합니다.")
    speak("안녕하세요! 함께 운동을 시작해볼까요?")
    
    cap = cv2.VideoCapture(0)  # 카메라 열기
    if not cap.isOpened():
        print("카메라를 찾을 수 없습니다.")
        speak("카메라를 찾을 수 없습니다.")
        return
    
    print("카메라를 켭니다...")
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        stage = "detection"  # 단계: detection -> raise -> hands_on_waist -> done
        detected = False
        fail_count = 0
        last_feedback_time = 0
        feedback_interval = 3  # 3초마다 피드백

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("카메라를 찾을 수 없습니다.")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # 사람 인식 단계
            if stage == "detection":
                if results.pose_landmarks:
                    if not detected:
                        print("인식 성공! 운동을 시작합니다.")
                        speak("운동을 시작합니다.")
                        stage = "raise"
                        detected = True
                        speak("첫 번째 동작입니다. 만세를 해보세요!")
                else:
                    print("인식 실패. 카메라 앞으로 와주세요.")
                    speak("카메라 앞으로 와주세요.")
                
                cv2.imshow("Camera Check", frame)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
                continue

            # 운동 동작 수행 단계
            if results.pose_landmarks:
                try:
                    landmarks = results.pose_landmarks.landmark
                    current_time = time.time()

                    # 좌측 팔 어깨-팔꿈치-손목 좌표
                    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                    # 팔 각도 계산
                    angle = calculate_angle(shoulder, elbow, wrist)

                    # 만세 동작
                    if stage == "raise":
                        if current_time - last_feedback_time >= feedback_interval:
                            if angle > 160 and wrist[1] < shoulder[1]:
                                print("만세 동작 성공!")
                                speak("정답! 축하합니다!")
                                stage = "hands_on_waist"
                                fail_count = 0
                                speak("두 번째 동작입니다. 허리에 손을 얹어보세요!")
                                time.sleep(2)
                            else:
                                fail_count += 1
                                print(f"만세 동작 오답 ({fail_count}/3)")
                                if fail_count >= 3:
                                    print("3회 실패, 괜찮아요. 다음 동작으로 넘어갑니다.")
                                    speak("괜찮아요, 다음 동작으로 넘어갈게요")
                                    stage = "hands_on_waist"
                                    fail_count = 0
                                    speak("두 번째 동작입니다. 허리에 손을 얹어보세요!")
                                    time.sleep(2)
                                else:
                                    speak("조금만 더 팔을 펴볼까요?")
                            last_feedback_time = current_time

                    # 허리에 손 얹기 동작
                    elif stage == "hands_on_waist":
                        if current_time - last_feedback_time >= feedback_interval:
                            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                            
                            if abs(wrist[1] - hip[1]) < 0.05:  # 손목-허리 y좌표 차이가 작으면 성공
                                print("허리에 손 얹기 성공!")
                                speak("정답! 축하합니다!")
                                stage = "done"
                                fail_count = 0
                                time.sleep(3)
                            else:
                                fail_count += 1
                                print(f"허리에 손 얹기 오답 ({fail_count}/3)")
                                if fail_count >= 3:
                                    print("3회 실패, 괜찮아요. 운동을 마칩니다.")
                                    speak("괜찮아요, 운동을 마칩니다.")
                                    stage = "done"
                                else:
                                    speak("다시 해보세요!")
                            last_feedback_time = current_time

                    # 운동 완료
                    if stage == "done":
                        print("모든 동작 완료")
                        speak("모든 운동이 끝났습니다. 수고하셨습니다!")
                        break

                except Exception as e:
                    print(f"좌표 추출 오류: {e}")
                    pass
            else:
                print("인식 실패. 카메라 앞으로 와주세요.")
            
            # 화면에 관절 표시
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            cv2.imshow('Exercise Mode', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("운동 모드 종료")