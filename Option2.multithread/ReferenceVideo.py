import cv2

def play_reference_video(ref, start_frame, end_frame, display_size):
    """
    참조 영상을 재생하는 함수
    ref: VideoCapture 객체
    start_frame: 시작 프레임
    end_frame: 종료 프레임  
    display_size: 표시 크기 (width, height)
    """
    window_name = "참조 영상"
    
    ref.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    while ref.isOpened():
        ret, frame = ref.read()
        if not ret:
            break
        
        current_frame = int(ref.get(cv2.CAP_PROP_POS_FRAMES))
        if current_frame > end_frame:
            break
        
        # 프레임 크기 조정
        if display_size:
            frame = cv2.resize(frame, display_size)
        
        cv2.imshow(window_name, frame)
        
        # 3초마다 멈춤 효과를 위한 지연
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    
    cv2.destroyWindow(window_name)