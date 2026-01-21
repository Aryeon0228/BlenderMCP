# BlenderMCP

**Blender 5.0.1을 위한 MCP(Model Context Protocol) 서버 - Windows 10 지원**

Claude Desktop에서 Blender를 직접 제어할 수 있게 해주는 MCP 서버입니다.

## 📋 요구사항

- **OS**: Windows 10
- **Blender**: 5.0.1 버전
- **Python**: 3.8 이상
- **Claude Desktop**: 최신 버전

## 🚀 설치 방법

### 1단계: Python 설치 확인

명령 프롬프트(CMD)에서 Python이 설치되어 있는지 확인:

```cmd
python --version
```

Python이 설치되어 있지 않다면 [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드하여 설치하세요.

### 2단계: 저장소 클론 또는 다운로드

```cmd
git clone https://github.com/yourusername/BlenderMCP.git
cd BlenderMCP
```

또는 ZIP 파일로 다운로드하여 압축 해제하세요.

### 3단계: 자동 설치 실행

```cmd
install.bat
```

이 스크립트는 자동으로:
- Python 패키지 설치 (`mcp`, `pydantic`)
- Blender 경로 확인
- 설치 완료 안내

### 4단계: Claude Desktop 설정

#### 4-1. 설정 파일 위치

Claude Desktop 설정 파일을 엽니다:

```
%APPDATA%\Claude\claude_desktop_config.json
```

탐색기 주소창에 위 경로를 붙여넣으면 파일을 찾을 수 있습니다.

#### 4-2. 설정 추가

`claude_desktop_config.json` 파일을 메모장으로 열고 다음 내용을 추가:

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": [
        "C:\\Users\\YourUsername\\BlenderMCP\\blender_mcp_server.py"
      ],
      "env": {
        "BLENDER_PATH": "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
      }
    }
  }
}
```

**⚠️ 중요**:
- `C:\\Users\\YourUsername\\BlenderMCP\\blender_mcp_server.py`를 **실제 설치 경로**로 변경하세요
- 블렌더 설치 경로가 다르다면 `BLENDER_PATH`도 수정하세요
- Windows 경로는 백슬래시를 두 번(`\\`) 사용해야 합니다

#### 4-3. Claude Desktop 재시작

Claude Desktop을 완전히 종료하고 다시 실행하세요.

## 🎨 사용 가능한 기능

MCP 서버가 제공하는 Blender 제어 도구:

### 1. `create_cube` - 큐브 생성
```
블렌더에 큐브를 생성합니다.
- name: 오브젝트 이름
- location: [x, y, z] 위치
- size: 크기
```

### 2. `create_sphere` - 구 생성
```
블렌더에 UV 구를 생성합니다.
- name: 오브젝트 이름
- location: [x, y, z] 위치
- radius: 반지름
- subdivisions: 세분화 수
```

### 3. `execute_python` - Python 코드 실행
```
블렌더에서 임의의 Python 코드를 실행합니다.
- code: 실행할 Python 코드
- background: 백그라운드 모드 (기본: true)
```

### 4. `render_scene` - 씬 렌더링
```
현재 블렌더 씬을 이미지로 렌더링합니다.
- output_path: 출력 파일 경로
- resolution_x: 가로 해상도 (기본: 1920)
- resolution_y: 세로 해상도 (기본: 1080)
- samples: 렌더 샘플 수 (기본: 128)
```

### 5. `save_blend_file` - .blend 파일 저장
```
현재 씬을 .blend 파일로 저장합니다.
- filepath: 저장 경로
```

### 6. `get_blender_info` - 블렌더 정보 확인
```
블렌더 버전 및 설치 정보를 가져옵니다.
```

### 7. `list_objects` - 오브젝트 목록
```
현재 씬의 모든 오브젝트를 나열합니다.
```

### 8. `delete_object` - 오브젝트 삭제
```
이름으로 오브젝트를 삭제합니다.
- name: 삭제할 오브젝트 이름
```

## 💡 사용 예시

Claude Desktop에서 다음과 같이 요청할 수 있습니다:

```
"블렌더에 큐브를 (0, 0, 0) 위치에 만들어줘"

"블렌더에 반지름 2인 구를 (2, 0, 0) 위치에 생성해줘"

"블렌더 씬에 있는 모든 오브젝트 목록을 보여줘"

"현재 씬을 C:\temp\output.png 로 렌더링해줘"

"블렌더에서 'import bpy; bpy.ops.mesh.primitive_cylinder_add()' 실행해줘"
```

## 🔧 문제 해결

### MCP 서버가 연결되지 않을 때

1. Claude Desktop을 완전히 재시작
2. 설정 파일 경로가 올바른지 확인
3. Python 패키지가 설치되었는지 확인: `pip list | findstr mcp`

### Blender 경로 오류

환경 변수를 확인하거나 시스템 환경 변수에 직접 추가:

```cmd
setx BLENDER_PATH "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
```

### Python 실행 오류

`blender_mcp_server.py` 파일을 직접 실행해서 오류 확인:

```cmd
python blender_mcp_server.py
```

## 📁 프로젝트 구조

```
BlenderMCP/
├── blender_mcp_server.py      # MCP 서버 메인 코드
├── package.json                # 프로젝트 메타데이터
├── requirements.txt            # Python 의존성
├── install.bat                 # 윈도우 설치 스크립트
├── mcp_config_example.json     # Claude Desktop 설정 예시
├── .env.example                # 환경 변수 예시
└── README.md                   # 이 파일
```

## 🤝 기여

이슈나 PR은 언제든 환영합니다!

## 📄 라이선스

MIT License