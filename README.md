# BlenderMCP

**Claude Desktop에서 Blender 5.0.1을 실시간으로 제어하는 MCP 서버 - Windows 10 지원**

Blender addon이 소켓 서버로 동작하여 Claude Desktop과 통신합니다. 빠른 응답 속도와 실시간 상호작용이 가능합니다.

## 📋 요구사항

- **OS**: Windows 10
- **Blender**: 5.0.1 버전
- **Python**: 3.8 이상
- **Claude Desktop**: 최신 버전

## 🎯 아키텍처

```
Claude Desktop → MCP Server (Python) → Socket (localhost:9876) → Blender Addon
```

**특징**:
- ✅ 빠른 응답 (Blender를 계속 실행 상태 유지)
- ✅ 실시간 뷰포트 스크린샷
- ✅ 양방향 통신
- ✅ 여러 명령을 연속으로 빠르게 실행

## 🚀 설치 방법

### 1단계: Python 설치 확인

명령 프롬프트(CMD)에서:

```cmd
python --version
```

Python이 없다면 [Python 공식 사이트](https://www.python.org/downloads/)에서 설치하세요.

### 2단계: 저장소 클론

```cmd
git clone https://github.com/Aryeon0228/BlenderMCP.git
cd BlenderMCP
```

### 3단계: Python 패키지 설치

```cmd
pip install -r requirements.txt
```

또는:

```cmd
python -m pip install -r requirements.txt
```

### 4단계: Blender Addon 설치

#### 4-1. addon.py 파일 확인
`BlenderMCP` 폴더에 `addon.py` 파일이 있는지 확인하세요.

#### 4-2. Blender에서 addon 설치

1. **Blender 5.0.1 실행**

2. **Edit → Preferences → Add-ons**

3. **Install 버튼 클릭**

4. `addon.py` 파일을 선택하고 **Install Add-on** 클릭

5. **검색창에 "MCP" 입력**하여 "Blender MCP Server" 찾기

6. **체크박스를 활성화**하여 addon 켜기

7. **Save Preferences** 클릭 (자동 로드되도록)

#### 4-3. 서버 시작 확인

- Blender 우측 사이드바에 **"MCP"** 탭이 생깁니다
- "Server Status: Running" 이 표시되면 정상 작동 중
- Port: 9876 확인

**서버가 자동 시작되지 않으면**:
- MCP 탭에서 "Start Server" 버튼 클릭

### 5단계: Claude Desktop 설정

#### 5-1. 설정 파일 열기

Windows 탐색기 주소창에 입력:

```
%APPDATA%\Claude
```

#### 5-2. claude_desktop_config.json 생성/수정

파일이 없으면 새로 만들고, 다음 내용 추가:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": [
        "C:\\Users\\김소연\\BlenderMCP\\blender_mcp_server.py"
      ],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

**⚠️ 중요**:
- 경로를 **실제 설치 위치**로 변경하세요
- Windows 경로는 백슬래시를 두 번(`\\`) 사용

#### 5-3. Claude Desktop 재시작

완전히 종료(작업 표시줄에서도)하고 다시 실행하세요.

## 🎨 사용 가능한 기능

### 장면 정보
- `get_scene_info` - 현재 씬의 모든 정보 조회
- `get_object_info` - 특정 객체의 상세 정보

### 객체 생성 및 조작
- `create_object` - 객체 생성 (cube, sphere, cylinder, cone, plane, torus)
- `delete_object` - 객체 삭제
- `move_object` - 객체 이동
- `scale_object` - 객체 크기 조정
- `rotate_object` - 객체 회전

### 재질 및 렌더링
- `set_material` - 재질 및 색상 설정
- `render_scene` - 씬 렌더링
- `get_viewport_screenshot` - 뷰포트 스크린샷 (실시간!)

### 고급 기능
- `execute_blender_code` - Python 코드 직접 실행 (bpy 접근)
- `save_blend_file` - .blend 파일 저장

## 💡 사용 예시

Claude Desktop에서:

```
"블렌더 씬 정보를 보여줘"

"블렌더에 빨간색 큐브를 (0, 0, 0)에 만들어줘"

"현재 블렌더 화면을 스크린샷으로 보여줘"

"Cube라는 이름의 객체를 (2, 0, 0)으로 이동해줘"

"블렌더에서 구를 만들고 파란색으로 칠해줘"
```

## 🔧 문제 해결

### "Connection Error" 발생

**원인**: Blender가 실행 중이지 않거나 addon이 비활성화됨

**해결**:
1. Blender 5.0.1 실행 확인
2. Blender에서 Edit → Preferences → Add-ons
3. "Blender MCP Server" addon 활성화 확인
4. MCP 탭에서 "Server Status: Running" 확인

### Addon이 보이지 않음

**해결**:
1. Blender를 완전히 종료하고 재실행
2. Preferences → Add-ons에서 "MCP" 검색
3. 없으면 addon.py 재설치
4. Blender 버전 확인 (5.0 이상 필요)

### MCP 서버가 연결되지 않음

**해결**:
1. Claude Desktop 완전 재시작
2. `claude_desktop_config.json` 경로 확인
3. Python 패키지 설치 확인: `pip list | findstr mcp`
4. MCP 서버 직접 실행 테스트:
   ```cmd
   cd C:\Users\김소연\BlenderMCP
   python blender_mcp_server.py
   ```

### 포트 충돌

다른 프로그램이 9876 포트를 사용 중이라면:

1. Blender addon에서 포트 변경 (addon.py 수정)
2. Claude Desktop 설정에서도 `BLENDER_PORT` 변경

## 📁 프로젝트 구조

```
BlenderMCP/
├── addon.py                        # Blender addon (소켓 서버)
├── blender_mcp_server.py          # MCP 서버 (소켓 클라이언트)
├── requirements.txt                # Python 의존성
├── package.json                    # 프로젝트 메타데이터
├── mcp_config_example.json         # Claude Desktop 설정 예시
├── .env.example                    # 환경 변수 예시
└── README.md                       # 이 파일
```

## 🔄 작동 원리

1. **Blender Addon**: Blender 내부에서 소켓 서버(localhost:9876) 실행
2. **MCP Server**: Claude Desktop이 실행하는 Python 프로세스
3. **통신**: JSON 기반 명령/응답 프로토콜
4. **실행**: Blender 메인 스레드에서 안전하게 명령 실행

## ⚡ 성능 비교

### 기존 방식 (subprocess):
```
명령 실행 → Blender 시작 (10초) → 실행 → 종료
```
**총 시간**: ~10-15초/명령

### 현재 방식 (socket):
```
명령 실행 → 즉시 실행 (Blender 이미 실행 중)
```
**총 시간**: ~0.1-1초/명령

**100배 이상 빠름!** 🚀

## 🤝 기여

이슈나 PR은 언제든 환영합니다!

원본 레포지토리: [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp)

## 📄 라이선스

MIT License

## 💬 지원

문제가 발생하면:
1. GitHub Issues에 보고
2. Blender 버전 확인 (5.0.1)
3. Python 버전 확인 (3.8+)
4. 로그 확인: `%APPDATA%\Claude\logs\mcp*.log`
