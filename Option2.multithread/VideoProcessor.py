import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from ThreadManager import ThreadManager, MessageType, ThreadMessage

class VideoProcessor:
    """영상 처리를 담당하는 별도 스레드 클래스"""
    
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.cap = None
        self.ref = None
        self.pose = None
        self.running = False
        
        # 영상 파일 경로들
        self.video_paths = [
            r"C:\Users\PC2403\Desktop\posture1.mp4",    # 첫 번째 자세
            r"C:\Users\PC2403\Desktop\posture2.mp4",   # 두 번째 자세
            r"C:\Users\PC2403\Desktop\posture3.mp4"       # 세 번째 자세
        ]
        
        # 상태 변수들
        self.current_video_index = 0
        self.video_retry_count = 0
        self.max_retry_count = 3
        self.last_check_time = 0
        self.last_fail_time = 0
        self.check_interval = 1  # 1초마다 체크 (5초 후 성공 체크를 위해)
        self.fail_interval = 5    # 5초마다 인식 실패 메시지
        
        # 자세별 특별 로직을 위한 변수들
        self.pose_detection_start_time = 0  # 자세 인식 시작 시간
        self.posture3_attempt_count = 0     # posture3 시도 횟수
        self.posture3_continuous_detection = False  # posture3에서 연속 인식 상태
        
    def calculate_angle(self, x, y, z):
        """세 점 사이 각도 계산"""
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
        
        yx = x - y
        yz = z - y
        
        cosine_angle = np.dot(yx, yz) / (np.linalg.norm(yx) * np.linalg.norm(yz))
        angle = np.arccos(cosine_angle)
        return int(np.degrees(angle))
    
    def initialize_camera_and_video(self):
        """카메라와 참조 영상 초기화"""
        print("[VIDEO] 카메라 0번에 연결 중...")
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print("[VIDEO] 카메라 0번을 열 수 없습니다.")
                print("[VIDEO] 다른 카메라 인덱스를 시도합니다...")
                
                # 다른 카메라 인덱스 시도
                for i in range(1, 4):
                    print(f"[VIDEO] 카메라 {i}번에 연결 시도...")
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        print(f"[VIDEO] 카메라 {i}번 연결 성공!")
                        break
                else:
                    print("[VIDEO] 사용 가능한 카메라를 찾을 수 없습니다.")
                    return False
            else:
                print("[VIDEO] 카메라 0번 연결 성공!")
        except Exception as e:
            print(f"[VIDEO] 카메라 초기화 오류: {e}")
            return False
        
        # 첫 번째 참조 영상 열기
        self.current_video_index = 0
        print(f"[VIDEO] 영상 파일 열기 시도: {self.video_paths[self.current_video_index]}")
        
        try:
            self.ref = cv2.VideoCapture(self.video_paths[self.current_video_index])
            
            if not self.ref.isOpened():
                print(f"[VIDEO] 영상 파일을 열 수 없습니다: {self.video_paths[self.current_video_index]}")
                print("[VIDEO] 영상 파일 경로를 확인해주세요.")
                if self.cap:
                    self.cap.release()
                return False
            else:
                print(f"[VIDEO] 영상 파일 열기 성공: {self.video_paths[self.current_video_index]}")
        except Exception as e:
            print(f"[VIDEO] 영상 파일 열기 오류: {e}")
            if self.cap:
                self.cap.release()
            return False
        
        # MediaPipe Pose 초기화
        print("[VIDEO] MediaPipe Pose 초기화 중...")
        try:
            self.pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
            print("[VIDEO] MediaPipe Pose 초기화 완료!")
        except Exception as e:
            print(f"[VIDEO] MediaPipe Pose 초기화 오류: {e}")
            if self.cap:
                self.cap.release()
            if self.ref:
                self.ref.release()
            return False
        
        return True
    
    def change_to_next_video(self):
        """다음 영상으로 순차 전환"""
        if self.ref:
            self.ref.release()
        
        # 다음 영상 인덱스 계산 (순환)
        next_index = (self.current_video_index + 1) % len(self.video_paths)
        new_video_path = self.video_paths[next_index]
        
        self.ref = cv2.VideoCapture(new_video_path)
        if self.ref.isOpened():
            print(f"[VIDEO] 다음 영상으로 전환: {new_video_path}")
            self.current_video_index = next_index
            return True
        else:
            print(f"[VIDEO] 영상 파일을 열 수 없습니다: {new_video_path}")
            # 실패시 원래 영상으로 복구
            fallback_ref = cv2.VideoCapture(self.video_paths[self.current_video_index])
            if fallback_ref.isOpened():
                self.ref = fallback_ref
                return False
            return False
    
    def analyze_posture(self, results, stage):
        """자세 분석 로직 (새로운 요구사항 적용)"""
        if not results.pose_landmarks:
            return False
        
        current_time = time.time()
        
        try:
            if stage == "posture1":
                # posture1: 인식 후 5초 후 자동 성공
                if self.pose_detection_start_time > 0:
                    elapsed_time = current_time - self.pose_detection_start_time
                    if elapsed_time >= 5.0:  # 5초 경과
                        print(f"[VIDEO] posture1: 5초 경과로 자동 성공 (경과시간: {elapsed_time:.1f}초)")
                        return True
                return False
                
            elif stage == "posture2":
                # posture2: 인식 후 5초 후 자동 성공
                if self.pose_detection_start_time > 0:
                    elapsed_time = current_time - self.pose_detection_start_time
                    if elapsed_time >= 5.0:  # 5초 경과
                        print(f"[VIDEO] posture2: 5초 경과로 자동 성공 (경과시간: {elapsed_time:.1f}초)")
                        return True
                return False
                
            elif stage == "posture3":
                # posture3: 연속 인식 상태에서만 카운트 증가
                if self.posture3_continuous_detection:
                    self.posture3_attempt_count += 1
                    print(f"[VIDEO] posture3: 연속 인식 상태에서 시도 횟수 {self.posture3_attempt_count}")
                    
                    if self.posture3_attempt_count == 1:
                        # 첫 번째 시도는 항상 실패
                        print("[VIDEO] posture3: 첫 번째 시도 - 실패 (음성 메시지 재생)")
                        print("[VIDEO] posture3: 5초 후 두 번째 시도 예정...")
                        return False
                    elif self.posture3_attempt_count == 2:
                        # 두 번째 시도는 항상 성공
                        print("[VIDEO] posture3: 두 번째 시도 - 성공!")
                        return True
                    else:
                        # 세 번째 이후 시도도 성공
                        print(f"[VIDEO] posture3: {self.posture3_attempt_count}번째 시도 - 성공")
                        return True
                else:
                    # 연속 인식 상태가 아니면 실패
                    print("[VIDEO] posture3: 연속 인식 상태가 아님 - 실패")
                    return False
                
        except Exception as e:
            print(f"[VIDEO] 자세 분석 오류: {e}")
            return False
        
        return False
    
    def process_video_frame(self, thread_manager):
        """영상 프레임 처리 메인 루프"""
        frame_count = 0
        detected = False
        
        while self.running and not thread_manager.is_shutdown_requested():
            # 메인 스레드로부터 메시지 확인
            message = thread_manager.get_message_from_main(timeout=0.01)
            if message:
                if message.msg_type == MessageType.SHUTDOWN:
                    print("[VIDEO] 종료 메시지 수신")
                    break
                elif message.msg_type == MessageType.NEXT_POSTURE:
                    # 다음 자세로 전환
                    self.change_to_next_video()
                    self.video_retry_count = 0
                    # 상태 초기화
                    self.pose_detection_start_time = 0
                    # posture3로 전환하는 경우 시도 횟수 및 연속 인식 상태 초기화
                    current_stage = thread_manager.shared_data.get('current_stage')
                    if current_stage == 'posture3':
                        self.posture3_attempt_count = 0
                        self.posture3_continuous_detection = False
                        print("[VIDEO] posture3로 전환 - 시도 횟수 및 연속 인식 상태 초기화")
                    print("[VIDEO] 다음 자세로 전환 - 상태 초기화")
                elif message.msg_type == MessageType.RESTART_VIDEO:
                    # 영상 재시작
                    if self.ref:
                        self.ref.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    # 상태 초기화 (posture3 제외)
                    current_stage = thread_manager.shared_data.get('current_stage')
                    if current_stage != 'posture3':
                        self.pose_detection_start_time = 0
            
            # 웹캠 프레임 읽기
            ret1, frame1 = self.cap.read()
            # 따라하기 영상 프레임 읽기
            ret2, frame2 = self.ref.read()
            
            frame_count += 1
            if frame_count % 100 == 0:  # 100프레임마다 상태 출력
                print(f"[VIDEO] 프레임 {frame_count}: 웹캠={ret1}, 참조영상={ret2}")
            
            if not ret1:
                print("[VIDEO] 웹캠 프레임 읽기 실패!")
                thread_manager.send_to_main_thread(MessageType.CAMERA_ERROR)
                break
            
            if not ret2:
                # 영상이 끝났을 때의 처리
                current_stage = thread_manager.shared_data.get('current_stage')
                video_completed = thread_manager.shared_data.get('video_completed')
                
                if video_completed:
                    # 자세가 완료되었으면 다음 영상으로 전환
                    print("[VIDEO] 자세 완료! 다음 영상으로 전환합니다.")
                    thread_manager.send_to_main_thread(MessageType.VIDEO_END, 
                                                     {'completed': True, 'stage': current_stage})
                    self.change_to_next_video()
                    self.video_retry_count = 0
                    thread_manager.shared_data.set('video_completed', False)
                else:
                    # 자세가 완료되지 않았으면 재시도
                    if self.video_retry_count < self.max_retry_count:
                        self.video_retry_count += 1
                        print(f"[VIDEO] 자세 미완료. 영상을 다시 재생합니다. ({self.video_retry_count}/{self.max_retry_count})")
                        time.sleep(3)
                        self.ref.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        # 최대 재시도 횟수 초과 시 다음 영상으로 전환
                        print("[VIDEO] 최대 재시도 횟수 초과. 다음 영상으로 전환합니다.")
                        thread_manager.send_to_main_thread(MessageType.VIDEO_END, 
                                                         {'completed': False, 'stage': current_stage})
                        self.change_to_next_video()
                        self.video_retry_count = 0
                
                ret2, frame2 = self.ref.read()
                if not ret2:
                    continue
            
            # 두 영상을 같은 크기로 맞추기
            frame1 = cv2.resize(frame1, (640, 480))
            frame2 = cv2.resize(frame2, (640, 480))
            
            # Mediapipe Pose 처리 (카메라 영상만 분석)
            image = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.pose.process(image)
            
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # MediaPipe 결과를 frame1에 반영
            frame1 = image.copy()
            
            # 사람 인식 확인
            if results.pose_landmarks:
                if not detected:
                    print("[VIDEO] 인식 성공")
                    thread_manager.send_to_main_thread(MessageType.POSE_DETECTED)
                    detected = True
                    thread_manager.shared_data.set('pose_detected', True)
                    thread_manager.shared_data.set('last_detection_time', time.time())
                    
                    # 자세 인식 시작 시간 기록 (posture1, posture2용)
                    current_stage = thread_manager.shared_data.get('current_stage')
                    if current_stage in ['posture1', 'posture2'] and self.pose_detection_start_time == 0:
                        self.pose_detection_start_time = time.time()
                        print(f"[VIDEO] {current_stage} 자세 인식 시작 시간 기록")
                    elif current_stage == 'posture3':
                        # posture3에서 연속 인식 상태 시작
                        if not self.posture3_continuous_detection:
                            self.posture3_continuous_detection = True
                            print("[VIDEO] posture3 연속 인식 상태 시작")
            else:
                if detected:  # 이전에 인식되었던 경우에만 메시지 출력
                    current_time = time.time()
                    if current_time - self.last_fail_time >= self.fail_interval:
                        print("[VIDEO] 인식 실패")
                        thread_manager.send_to_main_thread(MessageType.POSE_LOST)
                        self.last_fail_time = current_time
                    detected = False
                    thread_manager.shared_data.set('pose_detected', False)
                    
                    # 인식 실패 시 자세 인식 시작 시간 초기화
                    self.pose_detection_start_time = 0
                    
                    # posture3에서 연속 인식 상태 초기화
                    current_stage = thread_manager.shared_data.get('current_stage')
                    if current_stage == 'posture3':
                        self.posture3_continuous_detection = False
                        print("[VIDEO] posture3 연속 인식 상태 초기화")
            
            # 자세별 다른 간격으로 자세 판정
            current_time = time.time()
            current_stage = thread_manager.shared_data.get('current_stage')
            
            # posture3는 5초마다, 나머지는 1초마다 체크
            check_interval = 5 if current_stage == 'posture3' else self.check_interval
            
            if detected and current_time - self.last_check_time >= check_interval:
                self.last_check_time = current_time
                
                # 자세 분석
                posture_success = self.analyze_posture(results, current_stage)
                
                if posture_success:
                    print(f"[VIDEO] {current_stage} 자세 성공!")
                    thread_manager.send_to_main_thread(MessageType.POSTURE_SUCCESS, 
                                                     {'stage': current_stage})
                    thread_manager.shared_data.update({
                        'video_completed': True,
                        'fail_count': 0
                    })
                else:
                    # posture1과 posture2는 사람 인식만 되면 성공하므로 실패 메시지를 자주 보내지 않음
                    if current_stage in ['posture1', 'posture2']:
                        print(f"[VIDEO] {current_stage} 사람 인식 대기 중...")
                        # posture1, posture2는 실패 메시지를 보내지 않음 (사람 인식만 되면 성공)
                    else:
                        print(f"[VIDEO] {current_stage} 자세 실패")
                        fail_count = thread_manager.shared_data.get('fail_count') + 1
                        thread_manager.shared_data.set('fail_count', fail_count)
                        thread_manager.send_to_main_thread(MessageType.POSTURE_FAIL, 
                                                         {'stage': current_stage, 'fail_count': fail_count})
            
            # 관절 그리기 (웹캠 영상에만)
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame1, 
                    results.pose_landmarks, 
                    mp.solutions.pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
            
            # 영상 크기 조정 (적당한 크기로 표시)
            scale_factor = 1.2  # 1.2배 크기로 조정
            height1, width1 = frame1.shape[:2]
            height2, width2 = frame2.shape[:2]
            
            # 프레임 크기 조정
            new_width1 = int(width1 * scale_factor)
            new_height1 = int(height1 * scale_factor)
            new_width2 = int(width2 * scale_factor)
            new_height2 = int(height2 * scale_factor)
            
            frame1_resized = cv2.resize(frame1, (new_width1, new_height1))
            frame2_resized = cv2.resize(frame2, (new_width2, new_height2))
            
            # 영상 결합 및 표시
            combined = cv2.hconcat([frame1_resized, frame2_resized])
            cv2.imshow("운동 모드 (왼쪽=웹캠/오른쪽=따라하기영상)", combined)
            
            # ESC 키(27) 또는 'q' 키로 종료
            key = cv2.waitKey(10) & 0xFF
            if key == 27 or key == ord('q'):
                print("[VIDEO] ESC 키를 눌러 영상 처리를 종료합니다.")
                thread_manager.send_to_main_thread(MessageType.SHUTDOWN)
                break
    
    def cleanup(self):
        """리소스 정리"""
        print("[VIDEO] 영상 처리 리소스 정리 중...")
        self.running = False
        
        if self.cap:
            self.cap.release()
        if self.ref:
            self.ref.release()
        if self.pose:
            self.pose.close()
        
        cv2.destroyAllWindows()
        print("[VIDEO] 영상 처리 리소스 정리 완료")

def video_processing_thread(thread_manager: ThreadManager):
    """영상 처리 스레드 메인 함수"""
    print("[VIDEO] 영상 처리 스레드 시작")
    
    video_processor = VideoProcessor()
    
    try:
        # 카메라와 영상 초기화
        if not video_processor.initialize_camera_and_video():
            thread_manager.send_to_main_thread(MessageType.CAMERA_ERROR)
            return
        
        video_processor.running = True
        thread_manager.shared_data.set('exercise_running', True)
        
        # 영상 처리 메인 루프
        video_processor.process_video_frame(thread_manager)
        
    except Exception as e:
        print(f"[VIDEO] 영상 처리 스레드 오류: {e}")
        thread_manager.send_to_main_thread(MessageType.CAMERA_ERROR, {'error': str(e)})
    
    finally:
        video_processor.cleanup()
        thread_manager.shared_data.set('exercise_running', False)
        print("[VIDEO] 영상 처리 스레드 종료")
