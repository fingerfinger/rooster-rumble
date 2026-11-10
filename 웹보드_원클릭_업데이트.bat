@echo off
chcp 65001 > nul
title ROOSTER RUMBLE 웹보드 원클릭 업데이트 & GitHub 배포

echo ================================================================
echo  🐓 ROOSTER RUMBLE 웹보드 원클릭 자동 업데이트
echo ================================================================
echo.

echo [1/3] 웹보드 문서 및 데이터 동기화 중...
python sync_webboard.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 동기화 중 오류가 발생했습니다. 파이썬 환경을 확인해 주세요.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] 변경된 파일 확인 중...
git status -s
echo.

set "COMMIT_MSG="
set /p "COMMIT_MSG=📝 커밋 메모를 입력하세요 (엔터 치면 자동 입력): "
if "%COMMIT_MSG%"=="" (
    set "COMMIT_MSG=docs: 웹보드 산출물 업데이트 (%DATE% %TIME:~0,5%)"
)

echo.
echo [3/3] GitHub로 푸시(배포) 중...
git add .

rem 변경사항이 없을 때 커밋 에러 방지
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ℹ️ 새로 변경되거나 추가된 파일이 없습니다. (이미 최신 상태)
    echo.
    pause
    exit /b 0
)

git commit -m "%COMMIT_MSG%"
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo  🎉 GitHub 배포가 성공적으로 완료되었습니다!
    echo  약 1~2분 후 아래 웹사이트에 자동으로 최신 내용이 반영됩니다:
    echo  👉 https://fingerfinger.github.io/rooster-rumble/
    echo ================================================================
) else (
    echo.
    echo ⚠️ GitHub 푸시 중 문제가 발생했습니다. 위 메시지를 확인해 주세요.
)

echo.
pause
