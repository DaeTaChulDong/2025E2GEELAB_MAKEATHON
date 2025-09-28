#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아두이노 응답 수신 예제 코드
ArduinoCommunication.py의 새로운 응답 수신 기능 사용법
"""

import time
from ArduinoCommunication import (
    initialize_arduino, 
    cleanup_arduino, 
    arduino_controller,
    control_led, 
    play_sound, 
    play_voice_guide, 
    play_specific_mp3
)

def example_basic_response():
    """기본 응답 수신 예제"""
    print("=== 기본 응답 수신 예제 ===")
    
    if initialize_arduino('COM3'):
        # 명령 전송 후 응답 대기
        print("LED 제어 명령 전송...")
        control_led(arduino_controller, 'green')
        
        # 응답 대기
        response = arduino_controller.wait_for_response("LED:", timeout=3.0)
        if response:
            print(f"응답 수신: {response}")
        else:
            print("응답 없음")
        
        cleanup_arduino()
    else:
        print("아두이노 연결 실패")

def example_callback_usage():
    """콜백 함수 사용 예제"""
    print("\n=== 콜백 함수 사용 예제 ===")
    
    if initialize_arduino('COM3'):
        # 콜백 함수 정의
        def my_callback(data):
            print(f"[콜백] 아두이노 응답: {data}")
        
        # 콜백 등록
        arduino_controller.add_response_callback(my_callback)
        
        # 여러 명령 전송
        print("여러 명령 전송 중...")
        control_led(arduino_controller, 'red')
        time.sleep(1)
        
        play_sound(arduino_controller, 'success')
        time.sleep(1)
        
        play_specific_mp3(arduino_controller, "0001")
        time.sleep(2)
        
        # 콜백 제거
        arduino_controller.remove_response_callback(my_callback)
        
        cleanup_arduino()
    else:
        print("아두이노 연결 실패")

def example_response_queue():
    """응답 큐 사용 예제"""
    print("\n=== 응답 큐 사용 예제 ===")
    
    if initialize_arduino('COM3'):
        # 로깅 비활성화 (콘솔 출력 줄이기)
        arduino_controller.set_logging(False)
        
        # 여러 명령 전송
        print("여러 명령 전송...")
        control_led(arduino_controller, 'yellow')
        play_sound(arduino_controller, 'start')
        play_voice_guide(arduino_controller, 'welcome')
        
        time.sleep(2)  # 응답 수집 대기
        
        # 모든 응답 가져오기
        print("수신된 모든 응답:")
        responses = arduino_controller.get_all_responses()
        for i, response in enumerate(responses, 1):
            print(f"  {i}. {response}")
        
        cleanup_arduino()
    else:
        print("아두이노 연결 실패")

def example_response_log():
    """응답 로그 사용 예제"""
    print("\n=== 응답 로그 사용 예제 ===")
    
    if initialize_arduino('COM3'):
        # 로깅 활성화
        arduino_controller.set_logging(True)
        
        # 명령들 실행
        print("명령 실행 중...")
        control_led(arduino_controller, 'green')
        time.sleep(1)
        
        play_sound(arduino_controller, 'fail')
        time.sleep(1)
        
        play_specific_mp3(arduino_controller, "0002")
        time.sleep(2)
        
        # 응답 로그 출력
        print("\n응답 로그:")
        log_entries = arduino_controller.get_response_log()
        for entry in log_entries:
            print(f"  {entry}")
        
        # 로그 초기화
        arduino_controller.clear_response_log()
        print("로그 초기화 완료")
        
        cleanup_arduino()
    else:
        print("아두이노 연결 실패")

def example_advanced_monitoring():
    """고급 모니터링 예제"""
    print("\n=== 고급 모니터링 예제 ===")
    
    if initialize_arduino('COM3'):
        # 특정 응답 패턴 감지 콜백
        def success_detector(data):
            if "success" in data.lower() or "완료" in data:
                print("🎉 성공 감지!")
        
        def error_detector(data):
            if "error" in data.lower() or "실패" in data or "fail" in data.lower():
                print("❌ 오류 감지!")
        
        # 콜백 등록
        arduino_controller.add_response_callback(success_detector)
        arduino_controller.add_response_callback(error_detector)
        
        # 시뮬레이션 명령들
        print("시뮬레이션 명령 실행...")
        control_led(arduino_controller, 'green')  # 성공 시뮬레이션
        time.sleep(1)
        
        play_sound(arduino_controller, 'success')  # 성공 사운드
        time.sleep(1)
        
        play_sound(arduino_controller, 'fail')     # 실패 사운드
        time.sleep(2)
        
        # 콜백 제거
        arduino_controller.remove_response_callback(success_detector)
        arduino_controller.remove_response_callback(error_detector)
        
        cleanup_arduino()
    else:
        print("아두이노 연결 실패")

def main():
    """메인 함수"""
    print("아두이노 응답 수신 예제")
    print("=" * 50)
    
    try:
        # 각 예제 실행
        example_basic_response()
        example_callback_usage()
        example_response_queue()
        example_response_log()
        example_advanced_monitoring()
        
        print("\n" + "=" * 50)
        print("모든 예제 완료!")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        cleanup_arduino()

if __name__ == "__main__":
    main()
