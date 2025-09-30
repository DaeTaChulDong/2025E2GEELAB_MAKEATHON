#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
내장 스피커 통신 모듈
아두이노 대신 컴퓨터의 내장 스피커를 사용하여 음성 안내 및 효과음 재생
"""

import os
import time
import threading
import random
from pathlib import Path

# TTS (Text-to-Speech) 라이브러리 - 비활성화 (print 사용)
# try:
#     import pyttsx3
#     TTS_AVAILABLE = True
# except ImportError:
#     print("[SPEAKER] pyttsx3가 설치되지 않았습니다. 'pip install pyttsx3' 명령으로 설치해주세요.")
#     TTS_AVAILABLE = False
TTS_AVAILABLE = False
print("[SPEAKER] TTS 비활성화 - print 출력 사용")

# MP3 파일 재생용
try:
    import pygame
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
    print("[SPEAKER] pygame 초기화 완료")
except ImportError:
    print("[SPEAKER] pygame이 설치되지 않았습니다. 'pip install pygame' 명령으로 설치해주세요.")
    PYGAME_AVAILABLE = False
except Exception as e:
    print(f"[SPEAKER] pygame 초기화 실패: {e}")
    PYGAME_AVAILABLE = False

class SpeakerController:
    """내장 스피커 제어 클래스"""
    
    def __init__(self):
        self.is_connected = True  # 내장 스피커는 항상 사용 가능
        self.tts_engine = None
        
        # 디버그 로그 파일 생성
        self.debug_log_path = Path(__file__).parent / "speaker_debug.log"
        
        # MP3 파일 경로 설정 (여러 방법으로 시도)
        self.mp3_files_path = self._find_mp3_directory()
        self.audio_files_path = Path(__file__).parent / "audio_files"  # 백업용
        
        # TTS 엔진 비활성화 (print로 대체)
        self.tts_engine = None
        print("[SPEAKER] TTS 대신 print 출력을 사용합니다.")
        
        # 오디오 파일 디렉토리 생성
        self.audio_files_path.mkdir(exist_ok=True)
        
        # MP3 파일 경로 확인 및 디버깅
        print(f"[SPEAKER] MP3 파일 경로 확인: {self.mp3_files_path}")
        print(f"[SPEAKER] 경로 타입: {type(self.mp3_files_path)}")
        print(f"[SPEAKER] 절대 경로: {self.mp3_files_path.absolute()}")
        
        if not self.mp3_files_path.exists():
            print(f"[SPEAKER] 경고: MP3 파일 경로가 존재하지 않습니다!")
            print(f"[SPEAKER] 해당 경로에 000n.mp3 파일들을 배치해주세요.")
            
            # 상위 디렉토리 확인
            parent_path = self.mp3_files_path.parent
            print(f"[SPEAKER] 상위 디렉토리 확인: {parent_path} (존재: {parent_path.exists()})")
        else:
            print(f"[SPEAKER] ✅ MP3 파일 경로 확인됨: {self.mp3_files_path}")
            
            # 디렉토리 내 MP3 파일 확인
            try:
                mp3_files = list(self.mp3_files_path.glob("*.mp3"))
                print(f"[SPEAKER] 발견된 MP3 파일 수: {len(mp3_files)}")
                
                if mp3_files:
                    print("[SPEAKER] 발견된 MP3 파일들:")
                    for mp3_file in sorted(mp3_files)[:5]:  # 처음 5개만 표시
                        print(f"[SPEAKER]   - {mp3_file.name}")
                    if len(mp3_files) > 5:
                        print(f"[SPEAKER]   ... 및 {len(mp3_files) - 5}개 더")
            except Exception as e:
                print(f"[SPEAKER] MP3 파일 검색 중 오류: {e}")
        
        # 백업용 TTS 메시지들 (MP3 파일이 없을 때 사용)
        self.backup_messages = {
            # MP3 파일 번호에 대응하는 메시지들
            "0001": "안녕하세요! 운동을 시작하겠습니다.",
            "0002": "오늘도 재밌게 운동해 볼까요?",
            "0003": "좋아요! 함께 즐겁게 운동해봐요.",
            "0004": "왼손으로 골반을 잡으세요.",
            "0005": "이 동작을 따라해보세요.",
            "0006": "잘하셨습니다! 성공입니다.",
            "0007": "모든 동작이 완료되었습니다!",
            "0008": "훌륭합니다! 다음 동작으로 넘어가겠습니다.",
            "0009": "오늘 하루 더 맑아질 거예요!",
            "0010": "운동이 모두 끝났습니다. 수고하셨습니다!",
            "0011": "조금 더 노력해보세요!",
            "0013": "팔을 더 펴주세요.",
            "0014": "다시 한번 시도해보세요.",
            "0015": "자세를 다시 확인해주세요.",
        }
        
        # 효과음 메시지
        self.sound_messages = {
            'start': "운동을 시작합니다!",
            'success': "성공했습니다!",
            'fail': "다시 시도해보세요.",
            'complete': "운동이 완료되었습니다!",
            'clap': "박수! 잘하셨습니다!"
        }
        
        # 음성 안내 메시지
        self.voice_messages = {
            'welcome': "환영합니다! 운동 프로그램에 오신 것을 환영합니다.",
            'exercise_start': "운동을 시작하겠습니다.",
            'follow_me': "저를 따라해보세요.",
            'success': "성공입니다! 잘하셨어요.",
            'fail': "아쉽네요. 다시 한번 해보세요.",
            'complete': "모든 운동이 완료되었습니다. 수고하셨습니다!",
            'goodbye': "오늘 운동은 여기까지입니다. 안녕히 가세요!"
        }
    
    def connect(self):
        """스피커 연결 (항상 성공)"""
        self.is_connected = True
        print("[SPEAKER] 내장 스피커 연결 완료")
        return True
    
    def disconnect(self):
        """스피커 연결 해제"""
        self.is_connected = False
        
        # TTS 엔진 정리
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        # pygame 정리
        if PYGAME_AVAILABLE:
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
            except Exception as e:
                print(f"[SPEAKER] pygame 정리 중 오류: {e}")
        
        print("[SPEAKER] 내장 스피커 연결 해제 완료")
    
    def _log(self, message):
        """디버그 로그 기록"""
        try:
            with open(self.debug_log_path, "a", encoding="utf-8") as f:
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except:
            pass
        
        # 콘솔에도 출력
        print(message)
    
    def _find_mp3_directory(self):
        """MP3 디렉토리를 찾는 메서드 (여러 경로 시도)"""
        # 절대 경로 직접 지정 (확실히 존재하는 경로)
        direct_path = Path(r"C:\Users\PC2403\Desktop\mp3")
        
        # 경로가 존재하면 바로 반환
        if direct_path.exists() and any(direct_path.glob("*.mp3")):
            self._log(f"[SPEAKER] ✅ 직접 경로로 MP3 디렉토리 발견: {direct_path}")
            return direct_path
        
        # 백업 경로들
        possible_paths = [
            Path(r"C:\Users\PC2403\Desktop\mp3"),  # 원본 경로
            Path("C:/Users/PC2403/Desktop/mp3"),   # 슬래시 구분자
            Path.home() / "Desktop" / "mp3",       # 홈 디렉토리 기준
            Path(__file__).parent / "mp3",         # 프로그램 폴더 내
        ]
        
        self._log("[SPEAKER] MP3 디렉토리 검색 중...")
        
        for i, path in enumerate(possible_paths, 1):
            self._log(f"[SPEAKER] {i}. 경로 시도: {path}")
            try:
                if path.exists():
                    # MP3 파일이 실제로 있는지 확인
                    mp3_files = list(path.glob("*.mp3"))
                    if mp3_files:
                        self._log(f"[SPEAKER] ✅ MP3 디렉토리 발견: {path} ({len(mp3_files)}개 파일)")
                        for mp3_file in sorted(mp3_files)[:5]:  # 처음 5개 파일만 로그
                            self._log(f"[SPEAKER]   - {mp3_file.name}")
                        return path
                    else:
                        self._log(f"[SPEAKER] ⚠️  디렉토리는 존재하지만 MP3 파일이 없음: {path}")
                else:
                    self._log(f"[SPEAKER] ❌ 경로가 존재하지 않음: {path}")
            except Exception as e:
                self._log(f"[SPEAKER] ❌ 경로 확인 오류: {path} - {e}")
        
        # 기본 경로 반환 (없어도 일단 반환)
        default_path = possible_paths[0]
        self._log(f"[SPEAKER] ⚠️  MP3 디렉토리를 찾지 못했습니다. 기본 경로 사용: {default_path}")
        return default_path
    
    def _find_mp3_file(self, mp3_filename):
        """특정 MP3 파일을 찾는 메서드 (여러 파일명 패턴 시도)"""
        # 디렉토리가 존재하지 않으면 None 반환
        if not self.mp3_files_path.exists():
            self._log(f"[SPEAKER] MP3 디렉토리가 존재하지 않음: {self.mp3_files_path}")
            return None
        
        # 다양한 파일명 패턴 시도
        possible_names = [
            f"{mp3_filename}.mp3",           # 0001.mp3
            f"{mp3_filename}.MP3",           # 0001.MP3 (대문자)
        ]
        
        # 숫자 변환 가능한 경우 추가 패턴
        try:
            num = int(mp3_filename)
            possible_names.extend([
                f"{num:d}.mp3",              # 1.mp3 (앞의 0 제거)
                f"{num:04d}.mp3",            # 0001.mp3 (재포맷)
                f"{num:04d}.MP3",            # 0001.MP3 (재포맷 + 대문자)
            ])
        except ValueError:
            pass
        
        self._log(f"[SPEAKER] {mp3_filename} 파일 검색 시도...")
        
        # 각 패턴으로 파일 찾기
        for i, filename in enumerate(possible_names, 1):
            try:
                file_path = self.mp3_files_path / filename
                self._log(f"[SPEAKER] {i}. 시도: {file_path}")
                
                if file_path.exists():
                    self._log(f"[SPEAKER] ✅ 파일 발견: {file_path}")
                    return file_path
                else:
                    self._log(f"[SPEAKER] ❌ 파일 없음: {filename}")
                    
            except Exception as e:
                self._log(f"[SPEAKER] ❌ 파일 확인 오류: {filename} - {e}")
                continue
        
        # 모든 패턴이 실패한 경우, 디렉토리 내 실제 파일들 확인
        self._log(f"[SPEAKER] 모든 패턴 실패. 디렉토리 내 파일 목록 확인...")
        try:
            all_files = list(self.mp3_files_path.iterdir())
            mp3_files = [f for f in all_files if f.suffix.lower() in ['.mp3']]
            
            self._log(f"[SPEAKER] 디렉토리 내 총 파일 수: {len(all_files)}")
            self._log(f"[SPEAKER] 디렉토리 내 MP3 파일 수: {len(mp3_files)}")
            
            if mp3_files:
                self._log("[SPEAKER] 실제 존재하는 MP3 파일들:")
                for mp3_file in sorted(mp3_files)[:10]:  # 최대 10개만 표시
                    self._log(f"[SPEAKER]   - {mp3_file.name}")
                    
                # 파일명에 요청한 번호가 포함된 파일 찾기
                for mp3_file in mp3_files:
                    if mp3_filename in mp3_file.name:
                        self._log(f"[SPEAKER] 🎯 부분 매칭 파일 발견: {mp3_file}")
                        return mp3_file
                        
        except Exception as e:
            self._log(f"[SPEAKER] 디렉토리 스캔 오류: {e}")
        
        self._log(f"[SPEAKER] ❌ {mp3_filename} 파일을 찾을 수 없습니다.")
        return None
    
    def speak_text(self, text, async_mode=True):
        """텍스트를 print로 출력 (TTS 대신)"""
        if not self.is_connected:
            return False
        
        def _speak():
            print(f"[SPEAKER] 🔊 음성 안내: {text}")
        
        if async_mode:
            # 비동기로 실행하여 메인 스레드를 블록하지 않음
            threading.Thread(target=_speak, daemon=True).start()
        else:
            _speak()
        
        return True
    
    def play_mp3_file(self, mp3_filename, async_mode=True):
        """MP3 파일을 직접 재생"""
        if not self.is_connected:
            return False
        
        def _play_mp3():
            try:
                # MP3 파일을 여러 방법으로 찾기
                mp3_path = self._find_mp3_file(mp3_filename)
                
                self._log(f"[SPEAKER] MP3 파일 재생 시도: {mp3_filename}")
                
                if mp3_path and mp3_path.exists():
                    file_size = mp3_path.stat().st_size
                    self._log(f"[SPEAKER] ✅ 파일 발견: {mp3_path}")
                    self._log(f"[SPEAKER] 파일 크기: {file_size:,} bytes")
                else:
                    self._log(f"[SPEAKER] ❌ MP3 파일을 찾을 수 없습니다: {mp3_filename}")
                    
                    # 디렉토리 내 파일 목록 확인
                    if self.mp3_files_path.exists():
                        try:
                            existing_files = list(self.mp3_files_path.glob("*.mp3"))
                            self._log(f"[SPEAKER] 디렉토리 내 MP3 파일 수: {len(existing_files)}")
                            if existing_files:
                                self._log("[SPEAKER] 존재하는 MP3 파일들:")
                                for existing_file in sorted(existing_files)[:5]:
                                    self._log(f"[SPEAKER]   - {existing_file.name}")
                        except Exception as e:
                            self._log(f"[SPEAKER] 파일 목록 확인 오류: {e}")
                    
                    # 백업: print로 대체
                    backup_message = self.backup_messages.get(mp3_filename, f"메시지 번호 {mp3_filename}")
                    self._log(f"[SPEAKER] 🔊 백업 메시지 출력: {backup_message}")
                    print(f"[SPEAKER] 🔊 음성 안내: {backup_message}")
                    return False
                
                if not PYGAME_AVAILABLE:
                    print("[SPEAKER] pygame을 사용할 수 없습니다. print로 대체합니다.")
                    backup_message = self.backup_messages.get(mp3_filename, f"메시지 번호 {mp3_filename}")
                    print(f"[SPEAKER] 🔊 음성 안내: {backup_message}")
                    return False
                
                print(f"[SPEAKER] 🎵 MP3 파일 재생 시작: {mp3_path.name}")
                
                # pygame으로 MP3 파일 재생
                try:
                    pygame.mixer.music.load(str(mp3_path))
                    pygame.mixer.music.play()
                    print(f"[SPEAKER] ✅ pygame 재생 시작됨")
                    
                    # 재생 완료까지 대기 (동기 모드인 경우)
                    if not async_mode:
                        print(f"[SPEAKER] 재생 완료 대기 중...")
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        print(f"[SPEAKER] 재생 완료")
                            
                except pygame.error as e:
                    print(f"[SPEAKER] ❌ pygame 재생 오류: {e}")
                    raise Exception(f"pygame 재생 실패: {e}")
                
                return True
                
            except Exception as e:
                print(f"[SPEAKER] MP3 재생 오류: {e}")
                # 오류 시 print 백업
                backup_message = self.backup_messages.get(mp3_filename, f"메시지 번호 {mp3_filename}")
                print(f"[SPEAKER] 🔊 백업 메시지 출력: {backup_message}")
                return False
        
        if async_mode:
            # 비동기로 실행하여 메인 스레드를 블록하지 않음
            threading.Thread(target=_play_mp3, daemon=True).start()
        else:
            _play_mp3()
        
        return True
    
    def play_system_sound(self, sound_type='default'):
        """시스템 효과음 재생"""
        if not self.is_connected:
            return False
        
        def _play_sound():
            try:
                if os.name == 'nt':  # Windows
                    import winsound
                    if sound_type == 'success':
                        winsound.MessageBeep(winsound.MB_OK)
                    elif sound_type == 'fail':
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    elif sound_type == 'complete':
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    else:
                        winsound.MessageBeep(winsound.MB_ICONINFORMATION)
                else:  # Linux/Mac
                    os.system('echo -e "\a"')  # 시스템 비프음
                
                print(f"[SPEAKER] 시스템 효과음 재생: {sound_type}")
            except Exception as e:
                print(f"[SPEAKER] 효과음 재생 오류: {e}")
        
        threading.Thread(target=_play_sound, daemon=True).start()
        return True

# 전역 스피커 객체
speaker_controller = None

def initialize_speaker():
    """스피커 초기화"""
    global speaker_controller
    print("[SPEAKER] 내장 스피커 초기화 시작")
    
    try:
        speaker_controller = SpeakerController()
        if speaker_controller.connect():
            print("[SPEAKER] 내장 스피커 초기화 완료")
            return True
        else:
            print("[SPEAKER] 내장 스피커 초기화 실패")
            speaker_controller = None
            return False
    except Exception as e:
        print(f"[SPEAKER] 스피커 초기화 중 오류: {e}")
        speaker_controller = None
        return False

def cleanup_speaker():
    """스피커 정리"""
    global speaker_controller
    if speaker_controller:
        print("[SPEAKER] 스피커 정리 시작...")
        speaker_controller.disconnect()
        speaker_controller = None
        print("[SPEAKER] 스피커 정리 완료")

# 기존 아두이노 함수들을 스피커 버전으로 대체
def play_sound(speaker, sound_type):
    """
    효과음 재생 (아두이노 호환)
    sound_type: 'start', 'success', 'fail', 'complete', 'clap'
    """
    if speaker and speaker.is_connected:
        message = speaker.sound_messages.get(sound_type, f"효과음: {sound_type}")
        speaker.speak_text(message)
        speaker.play_system_sound(sound_type)
        return True
    return False

def play_voice_guide(speaker, message_type):
    """
    음성 안내 재생 (아두이노 호환)
    message_type: 'welcome', 'exercise_start', 'follow_me', 'success', 'fail', 'complete'
    """
    if speaker and speaker.is_connected:
        message = speaker.voice_messages.get(message_type, f"음성 안내: {message_type}")
        speaker.speak_text(message)
        return True
    return False

def control_led(speaker, led_state):
    """
    LED 제어 (스피커에서는 음성으로 상태 안내)
    led_state: 'green', 'off'
    """
    if speaker and speaker.is_connected:
        if led_state == 'green':
            message = "시작합니다!"
            speaker.speak_text(message)
        elif led_state == 'off':
            message = "완료되었습니다."
            speaker.speak_text(message)
        return True
    return False

def play_random_mp3(speaker):
    """
    랜덤 MP3 파일 재생 (스피커 버전)
    """
    if speaker and speaker.is_connected:
        mp3_numbers = ['0001', '0002', '0003', '0004']
        selected = random.choice(mp3_numbers)
        return play_specific_mp3(speaker, selected)
    return False

def play_specific_mp3(speaker, mp3_file):
    """
    특정 MP3 파일 재생 (실제 MP3 파일 사용)
    mp3_file: 재생할 MP3 파일명 (예: "0001", "0002", "0003", "0004")
    """
    if not speaker or not speaker.is_connected:
        print("[SPEAKER] 스피커가 연결되지 않았습니다.")
        return False
    
    # MP3 파일명 정규화
    if isinstance(mp3_file, int):
        mp3_filename = f"{mp3_file:04d}"
    else:
        mp3_filename = str(mp3_file).zfill(4) if str(mp3_file).isdigit() else str(mp3_file)
    
    print(f"[SPEAKER] MP3 재생 요청: {mp3_filename}")
    
    # 직접 경로로 파일 확인 및 재생 시도
    try:
        from pathlib import Path
        
        # 직접 경로 지정 - 확실히 존재하는 경로
        mp3_path = Path(r"C:\Users\PC2403\Desktop\mp3") / f"{mp3_filename}.mp3"
        print(f"[SPEAKER] 파일 경로 확인: {mp3_path}")
        print(f"[SPEAKER] 파일 존재 여부: {mp3_path.exists()}")
        
        if mp3_path.exists():
            file_size = mp3_path.stat().st_size
            print(f"[SPEAKER] 파일 크기: {file_size:,} bytes")
            
            # pygame으로 직접 재생
            if PYGAME_AVAILABLE:
                try:
                    import pygame
                    if pygame.mixer.get_init():
                        pygame.mixer.music.load(str(mp3_path))
                        pygame.mixer.music.play()
                        print(f"[SPEAKER] ✅ {mp3_filename}.mp3 재생 시작됨")
                        return True
                    else:
                        print("[SPEAKER] pygame.mixer가 초기화되지 않았습니다.")
                except Exception as e:
                    print(f"[SPEAKER] pygame 재생 오류: {e}")
            else:
                print("[SPEAKER] pygame을 사용할 수 없습니다.")
        else:
            print(f"[SPEAKER] ❌ 파일이 존재하지 않습니다: {mp3_path}")
            
            # 디렉토리 내 실제 파일들 확인
            mp3_dir = Path(r"C:\Users\PC2403\Desktop\mp3")
            if mp3_dir.exists():
                existing_files = list(mp3_dir.glob("*.mp3"))
                print(f"[SPEAKER] 디렉토리 내 MP3 파일 수: {len(existing_files)}")
                if existing_files:
                    print("[SPEAKER] 존재하는 파일들:")
                    for f in sorted(existing_files)[:5]:
                        print(f"[SPEAKER]   - {f.name}")
            
    except Exception as e:
        print(f"[SPEAKER] 직접 재생 시도 오류: {e}")
    
    # 기존 방식으로 폴백
    print("[SPEAKER] 기존 방식으로 재생 시도...")
    return speaker.play_mp3_file(mp3_filename, async_mode=True)

# 테스트 함수
def test_speaker_connection():
    """스피커 연결 테스트"""
    if initialize_speaker():
        print("스피커 연결 테스트 시작...")
        
        # TTS 테스트
        play_specific_mp3(speaker_controller, "0001")
        time.sleep(2)
        
        # 효과음 테스트
        play_sound(speaker_controller, "success")
        time.sleep(2)
        
        # LED 상태 안내 테스트
        control_led(speaker_controller, "green")
        time.sleep(2)
        control_led(speaker_controller, "off")
        
        cleanup_speaker()
        print("스피커 연결 테스트 완료")
    else:
        print("스피커 연결 실패")

if __name__ == "__main__":
    # 단독 실행시 테스트
    print("내장 스피커 통신 테스트 시작")
    test_speaker_connection()
