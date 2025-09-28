#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아두이노 실시간 모니터링 코드
아두이노에서 오는 모든 메시지를 실시간으로 출력
"""

import time
import sys
from ArduinoCommunication import initialize_arduino, cleanup_arduino, arduino_controller

def monitor_arduino():
    """아두이노 실시간 모니터링"""
    print("아두이노 실시간 모니터링 시작")
    print("아두이노에서 오는 모든 메시지를 표시합니다.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    try:
        while True:
            if arduino_controller and arduino_controller.is_connected:
                response = arduino_controller.read_data()
                if response:
                    print(f"[{time.strftime('%H:%M:%S')}] {response}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n모니터링을 종료합니다.")

def main():
    """메인 함수"""
    # 아두이노 초기화
    print("아두이노 연결 시도...")
    if not initialize_arduino('COM3'):  # 포트는 환경에 맞게 수정
        print("아두이노 연결 실패! 포트를 확인해주세요.")
        return
    
    print("아두이노 연결 성공!")
    
    try:
        monitor_arduino()
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        cleanup_arduino()

if __name__ == "__main__":
    main()
