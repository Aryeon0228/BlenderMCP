@echo off
REM Blender MCP Server 설치 스크립트 (Windows 10)

echo ========================================
echo Blender MCP Server 설치
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python 패키지 설치 중...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [오류] 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [2/3] 블렌더 경로 확인 중...
set "DEFAULT_BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"

if exist "%DEFAULT_BLENDER_PATH%" (
    echo 블렌더 발견: %DEFAULT_BLENDER_PATH%
) else (
    echo [경고] 기본 경로에서 블렌더를 찾을 수 없습니다.
    echo 블렌더 경로를 환경변수 BLENDER_PATH에 설정해주세요.
    echo 예: set BLENDER_PATH=C:\Your\Path\To\blender.exe
)

echo.
echo [3/3] 설치 완료!
echo.
echo ========================================
echo 다음 단계:
echo ========================================
echo 1. Claude Desktop 설정 파일을 편집하세요:
echo    %APPDATA%\Claude\claude_desktop_config.json
echo.
echo 2. 아래 내용을 mcpServers 섹션에 추가하세요:
echo    (mcp_config_example.json 파일 참조)
echo.
echo 3. Claude Desktop을 재시작하세요.
echo ========================================
echo.
pause
