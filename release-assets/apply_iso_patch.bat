@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"

set "SOURCE_ISO=Breath of Fire III.iso"
set "PATCH_FILE=BOF3_KR_fontimage_v0.4.2-alpha.iso.xdelta"
set "OUTPUT_ISO=BOF3_KR_fontimage_v0.4.2-alpha.iso"

if not exist "%SOURCE_ISO%" (
  echo [오류] 원본 ISO "%SOURCE_ISO%" 파일을 이 폴더에 넣어 주세요.
  echo        원본 ISO MD5: C7081C9C0865ECAEB6F4D2A42F865528
  pause
  exit /b 1
)

if not exist "%PATCH_FILE%" (
  echo [오류] 패치 파일 "%PATCH_FILE%"을 찾을 수 없습니다.
  pause
  exit /b 1
)

if not exist "xdelta.exe" (
  echo [오류] xdelta.exe를 찾을 수 없습니다.
  pause
  exit /b 1
)

if exist "%OUTPUT_ISO%" del /f /q "%OUTPUT_ISO%"

echo xdelta 패치를 적용합니다...
"xdelta.exe" -f -d -s "%SOURCE_ISO%" "%PATCH_FILE%" "%OUTPUT_ISO%"
if errorlevel 1 (
  echo [오류] ISO 패치 적용에 실패했습니다.
  pause
  exit /b 1
)

echo.
echo 완료: "%OUTPUT_ISO%"
echo 패치 후 ISO MD5는 checksums.md의 값을 확인해 주세요.
pause
