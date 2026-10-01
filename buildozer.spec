# Buildozer spec - 2장 까기 카드 게임
# main.py, *.wav 파일들과 같은 폴더에 넣고 GitHub에 푸시하면
# GitHub Actions가 자동으로 APK를 만들어줍니다.

[app]

# 앱 제목 (폰에 표시되는 이름)
title = 2장 까기

# 패키지명 (영문 소문자, 점 없이)
package.name = cardgame2jang

# 도메인 (영문, 역순)
package.domain = org.yeongmin

# 소스 코드 위치 (. = 이 폴더)
source.dir = .

# 포함할 파일 확장자 (wav 필수!)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav

# 제외할 파일
source.exclude_exts = spec,yml,md,txt

# 진입점 파일 (반드시 main.py)
source.main = main.py

# 버전
version = 0.1
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# 필요한 파이썬 패키지 (plyer = 진동 기능)
requirements = python3,kivy,plyer

# 화면 방향: portrait(세로 고정)
orientation = portrait

# 전체화면 여부 (0 = 상태바 표시)
fullscreen = 0

# 안드로이드 권한 (진동)
android.permissions = VIBRATE

# 타겟 API (2026년 Play 스토어 기준: 36)
android.api = 36

# 최소 API
android.minapi = 24

# NDK 버전
android.ndk = 25b

# 아키텍처 (64비트 필수)
android.archs = arm64-v8a, armeabi-v7a

# SDK 라이선스 자동 동의
android.accept_sdk_license = True

[buildozer]

# 빌드 로그 레벨 (2 = 상세)
log_level = 2

# 루트 경고 무시
warn_on_root = 1
