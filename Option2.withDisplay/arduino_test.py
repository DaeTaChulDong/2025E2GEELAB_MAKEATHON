#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아두이노 통신 테스트 코드
ArduinoCommunication.py 라이브러리를 사용하여 아두이노와 통신 테스트
"""

import time
import sys
from ArduinoCommunication import (
    initialize_arduino, 
    cleanup_arduino, 
    arduino_controller,
    control_led, 
    play_sound, 
    play_voice_guide, 
    play_random_mp3, 
    play_specific_mp3
)

def test_led_controls():
    """LED 제어 테스트 (5번 핀, 녹색 LED만)"""
    print("\n=== LED 제어 테스트 (Pin 5, Green LED) ===")
    
    led_states = ['green', 'off']
    
    for state in led_states:
        if state == 'off':
            print(f"녹색 LED 끄기...")
        else:
            print(f"녹색 LED 켜기...")
        control_led(arduino_controller, state)
        time.sleep(2)
    
    print("LED 테스트 완료 (녹색 LED만 지원)\n")

def test_sound_controls():
    """사운드 제어 테스트"""
    print("\n=== 사운드 제어 테스트 ===")
    
    sound_types = ['start', 'success', 'fail', 'clap', 'complete']
    
    for sound_type in sound_types:
        print(f"사운드 {sound_type} 재생...")
        play_sound(arduino_controller, sound_type)
        time.sleep(3)
    
    print("사운드 테스트 완료\n")

def test_voice_guides():
    """음성 안내 테스트"""
    print("\n=== 음성 안내 테스트 ===")
    
    voice_types = ['welcome', 'follow_me', 'success', 'fail', 'complete', 'goodbye']
    
    for voice_type in voice_types:
        print(f"음성 안내 {voice_type} 재생...")
        play_voice_guide(arduino_controller, voice_type)
        time.sleep(2)
    
    print("음성 안내 테스트 완료\n")

def test_mp3_controls():
    """MP3 제어 테스트"""
    print("\n=== MP3 제어 테스트 ===")
    
    # 랜덤 MP3 테스트
    print("랜덤 MP3 재생 테스트...")
    for i in range(3):
        print(f"랜덤 MP3 {i+1}/3 재생...")
        play_random_mp3(arduino_controller)
        time.sleep(3)
    
    # 특정 MP3 파일 테스트
    print("\n특정 MP3 파일 테스트...")
    mp3_files = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', 
                 '0013', '0014', '0015', '0100', '0200']
    
    for mp3_file in mp3_files:
        print(f"MP3 파일 {mp3_file}.mp3 재생...")
        play_specific_mp3(arduino_controller, mp3_file)
        time.sleep(2)
    
    print("MP3 테스트 완료\n")

def test_combined_sequence():
    """통합 시퀀스 테스트 (실제 운동 프로그램과 유사)"""
    print("\n=== 통합 시퀀스 테스트 ===")
    
    # 운동 시작 시퀀스
    print("1. 운동 시작 시퀀스")
    control_led(arduino_controller, 'blue')
    play_specific_mp3(arduino_controller, "0001")
    time.sleep(2)
    
    play_specific_mp3(arduino_controller, "0002")
    time.sleep(2)
    
    play_specific_mp3(arduino_controller, "0003")
    time.sleep(2)
    
    # posture1 시퀀스
    print("2. Posture1 시퀀스")
    play_specific_mp3(arduino_controller, "0005")
    time.sleep(2)
    
    # 성공 시뮬레이션
    print("3. 성공 시뮬레이션")
    control_led(arduino_controller, 'green')
    play_specific_mp3(arduino_controller, "0008")
    play_voice_guide(arduino_controller, 'success')
    play_sound(arduino_controller, 'success')
    time.sleep(3)
    
    # posture2 시퀀스
    print("4. Posture2 시퀀스")
    play_specific_mp3(arduino_controller, "0004")
    time.sleep(2)
    
    # 성공 시뮬레이션
    print("5. 성공 시뮬레이션")
    play_specific_mp3(arduino_controller, "0100")
    time.sleep(2)
    
    # posture3 시퀀스
    print("6. Posture3 시퀀스")
    play_specific_mp3(arduino_controller, "0005")
    play_specific_mp3(arduino_controller, "0006")
    time.sleep(3)
    
    # 실패 시뮬레이션
    print("7. 실패 시뮬레이션")
    control_led(arduino_controller, 'red')
    play_specific_mp3(arduino_controller, "0015")
    play_voice_guide(arduino_controller, 'fail')
    play_sound(arduino_controller, 'fail')
    time.sleep(3)
    
    # 운동 완료 시퀀스
    print("8. 운동 완료 시퀀스")
    control_led(arduino_controller, 'green')
    play_specific_mp3(arduino_controller, "0200")
    play_voice_guide(arduino_controller, 'complete')
    play_sound(arduino_controller, 'complete')
    time.sleep(3)
    
    # 종료
    control_led(arduino_controller, 'off')
    print("통합 시퀀스 테스트 완료\n")

def monitor_arduino_responses():
    """아두이노 응답 모니터링"""
    print("\n=== 아두이노 응답 모니터링 ===")
    print("아두이노에서 오는 메시지를 모니터링합니다...")
    print("(5초간 모니터링 후 자동으로 다음 테스트로 진행)")
    
    start_time = time.time()
    while time.time() - start_time < 5:
        if arduino_controller and arduino_controller.is_connected:
            response = arduino_controller.read_data()
            if response:
                print(f"아두이노 응답: {response}")
        time.sleep(0.1)

def main():
    """메인 테스트 함수"""
    print("아두이노 통신 테스트 시작")
    print("=" * 50)
    
    # 아두이노 초기화
    print("아두이노 연결 시도...")
    if not initialize_arduino('COM3'):  # 포트는 환경에 맞게 수정
        print("아두이노 연결 실패! 포트를 확인해주세요.")
        print("사용 가능한 포트: COM3, COM4, COM5 등")
        return
    
    print("아두이노 연결 성공!")
    
    try:
        # 각 테스트 실행
        test_led_controls()
        test_sound_controls()
        test_voice_guides()
        test_mp3_controls()
        test_combined_sequence()
        
        # 아두이노 응답 모니터링
        monitor_arduino_responses()
        
        print("=" * 50)
        print("모든 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
    finally:
        # 정리
        print("아두이노 연결 해제...")
        cleanup_arduino()
        print("테스트 종료")

if __name__ == "__main__":
    main()
