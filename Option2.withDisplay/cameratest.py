import cv2

# 0번 카메라 (Logitech 웹캠) 열기
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows에서는 CAP_DSHOW 옵션 추천

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

print("웹캠이 열렸습니다. ESC 키를 누르면 종료됩니다.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 화면에 출력
    cv2.imshow("Webcam Test - Logitech", frame)

    # ESC(27) 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        print("테스트 종료")
        break

cap.release()
cv2.destroyAllWindows()
