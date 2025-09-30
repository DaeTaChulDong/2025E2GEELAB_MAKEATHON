import threading
import queue
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, Dict

class MessageType(Enum):
    """스레드 간 메시지 타입"""
    # 영상 처리 -> 메인 스레드
    POSE_DETECTED = "pose_detected"
    POSE_LOST = "pose_lost"
    POSTURE_SUCCESS = "posture_success"
    POSTURE_FAIL = "posture_fail"
    VIDEO_END = "video_end"
    CAMERA_ERROR = "camera_error"
    
    # 메인 스레드 -> 영상 처리
    START_EXERCISE = "start_exercise"
    STOP_EXERCISE = "stop_exercise"
    NEXT_POSTURE = "next_posture"
    RESTART_VIDEO = "restart_video"
    
    # 시스템 메시지
    SHUTDOWN = "shutdown"

@dataclass
class ThreadMessage:
    """스레드 간 메시지 구조"""
    msg_type: MessageType
    data: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class ThreadSafeData:
    """스레드 간 안전한 데이터 공유를 위한 클래스"""
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            'pose_detected': False,
            'current_stage': 'posture1',
            'video_completed': False,
            'exercise_running': False,
            'current_video_index': 0,
            'fail_count': 0,
            'last_detection_time': 0
        }
    
    def get(self, key: str) -> Any:
        """안전하게 데이터 읽기"""
        with self._lock:
            return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """안전하게 데이터 쓰기"""
        with self._lock:
            self._data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """여러 데이터를 한번에 업데이트"""
        with self._lock:
            self._data.update(updates)
    
    def get_all(self) -> Dict[str, Any]:
        """모든 데이터 복사본 반환"""
        with self._lock:
            return self._data.copy()

class ThreadManager:
    """스레드 관리 클래스"""
    def __init__(self):
        # 메시지 큐 (스레드 간 통신)
        self.main_to_video_queue = queue.Queue()  # 메인 -> 영상처리
        self.video_to_main_queue = queue.Queue()  # 영상처리 -> 메인
        
        # 공유 데이터
        self.shared_data = ThreadSafeData()
        
        # 스레드 객체들
        self.video_thread = None
        self.arduino_thread = None
        
        # 종료 플래그
        self._shutdown_flag = threading.Event()
    
    def send_to_video_thread(self, msg_type: MessageType, data: Optional[Dict[str, Any]] = None):
        """영상 처리 스레드로 메시지 전송"""
        message = ThreadMessage(msg_type, data)
        self.main_to_video_queue.put(message)
        print(f"[THREAD] 영상 스레드로 메시지 전송: {msg_type.value}")
    
    def send_to_main_thread(self, msg_type: MessageType, data: Optional[Dict[str, Any]] = None):
        """메인 스레드로 메시지 전송"""
        message = ThreadMessage(msg_type, data)
        self.video_to_main_queue.put(message)
        print(f"[THREAD] 메인 스레드로 메시지 전송: {msg_type.value}")
    
    def get_message_from_video(self, timeout: float = 0.1) -> Optional[ThreadMessage]:
        """영상 처리 스레드로부터 메시지 받기"""
        try:
            return self.video_to_main_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_message_from_main(self, timeout: float = 0.1) -> Optional[ThreadMessage]:
        """메인 스레드로부터 메시지 받기"""
        try:
            return self.main_to_video_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def start_video_thread(self, target_function, *args, **kwargs):
        """영상 처리 스레드 시작"""
        if self.video_thread and self.video_thread.is_alive():
            print("[THREAD] 영상 처리 스레드가 이미 실행 중입니다.")
            return False
        
        self._shutdown_flag.clear()
        self.video_thread = threading.Thread(
            target=target_function, 
            args=(self,) + args,
            kwargs=kwargs,
            daemon=True,
            name="VideoProcessingThread"
        )
        self.video_thread.start()
        print("[THREAD] 영상 처리 스레드 시작됨")
        return True
    
    def start_arduino_thread(self, target_function, *args, **kwargs):
        """아두이노 통신 스레드 시작 (필요시)"""
        if self.arduino_thread and self.arduino_thread.is_alive():
            print("[THREAD] 아두이노 스레드가 이미 실행 중입니다.")
            return False
        
        self.arduino_thread = threading.Thread(
            target=target_function,
            args=(self,) + args,
            kwargs=kwargs,
            daemon=True,
            name="ArduinoThread"
        )
        self.arduino_thread.start()
        print("[THREAD] 아두이노 스레드 시작됨")
        return True
    
    def shutdown(self):
        """모든 스레드 종료"""
        print("[THREAD] 스레드 종료 시작...")
        self._shutdown_flag.set()
        
        # 종료 메시지 전송
        self.send_to_video_thread(MessageType.SHUTDOWN)
        
        # 스레드 종료 대기
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=5.0)
            if self.video_thread.is_alive():
                print("[THREAD] 영상 처리 스레드 강제 종료")
        
        if self.arduino_thread and self.arduino_thread.is_alive():
            self.arduino_thread.join(timeout=2.0)
            if self.arduino_thread.is_alive():
                print("[THREAD] 아두이노 스레드 강제 종료")
        
        print("[THREAD] 모든 스레드 종료 완료")
    
    def is_shutdown_requested(self) -> bool:
        """종료 요청 여부 확인"""
        return self._shutdown_flag.is_set()

# 전역 스레드 매니저 인스턴스
thread_manager = ThreadManager()
