# 블렌더 MCP 연결 문제 해결 가이드

## 🔍 연결이 안될 때 체크리스트

### 1단계: Blender Addon 확인

#### 확인 사항
```
✓ Blender 5.0.1 실행 중인가?
✓ MCP addon이 설치되어 있나?
✓ MCP addon이 활성화되어 있나?
✓ MCP 서버가 실행 중인가?
```

#### 확인 방법

1. **Blender 실행 확인**
   - Blender가 열려있어야 합니다

2. **Addon 설치 확인**
   - `Edit > Preferences > Add-ons` 메뉴
   - 검색창에 "MCP" 입력
   - "Blender MCP Server" 항목이 있어야 합니다

3. **Addon 활성화 확인**
   - "Blender MCP Server" 옆 체크박스가 체크되어 있어야 합니다
   - 체크되지 않았다면 체크하세요

4. **서버 실행 확인**
   - 3D 뷰포트 우측 사이드바 (N 키로 토글)
   - **"MCP"** 탭 찾기
   - **"Server Status: Running"** 표시 확인
   - **"Port: 9876"** 표시 확인

**서버가 실행 중이 아니라면:**
- "Start Server" 버튼 클릭
- Blender 시스템 콘솔 확인: `Window > Toggle System Console`
- 콘솔에 "Blender MCP Server started on localhost:9876" 메시지 확인

---

### 2단계: Python 경로 확인

#### Windows 사용자

**명령 프롬프트(CMD)에서 실행:**

```cmd
where python
```

**예상 출력:**
```
C:\Users\사용자이름\AppData\Local\Programs\Python\Python311\python.exe
```

**이 경로를 기억하세요!** Claude Desktop 설정에 사용됩니다.

#### Linux/Mac 사용자

```bash
which python3
```

---

### 3단계: blender_mcp_server.py 경로 확인

**프로젝트 폴더로 이동:**

```cmd
cd C:\Users\사용자이름\BlenderMCP
dir blender_mcp_server.py
```

**또는 Linux/Mac:**

```bash
cd ~/BlenderMCP
ls -la blender_mcp_server.py
```

**파일이 있는지 확인하고 전체 경로를 기록하세요.**

---

### 4단계: Claude Desktop 설정 확인

#### 설정 파일 위치

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

#### 올바른 설정 형식

**중요: 현재 프로젝트는 ahujasid/blender-mcp와 다른 방식입니다!**

**✅ 올바른 설정 (이 프로젝트용):**

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": [
        "C:\\Users\\사용자이름\\BlenderMCP\\blender_mcp_server.py"
      ],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

**❌ 잘못된 설정 (ahujasid/blender-mcp용 - 이 프로젝트에서는 작동하지 않음):**

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

#### 설정 체크포인트

1. **경로 구분자**
   - Windows: 백슬래시 두 번 `\\` 사용
   - Linux/Mac: 슬래시 `/` 사용

2. **절대 경로 사용**
   - ❌ `args": ["blender_mcp_server.py"]`
   - ✅ `args": ["C:\\Users\\...\\blender_mcp_server.py"]`

3. **Python 명령어**
   - Windows: `"command": "python"` 또는 `"python3"`
   - Linux/Mac: `"command": "python3"`

4. **JSON 문법**
   - 중괄호, 대괄호, 쉼표 확인
   - 마지막 항목 뒤에는 쉼표 없음

---

### 5단계: 직접 연결 테스트

#### 테스트 1: Blender 서버만 테스트

**명령 프롬프트/터미널에서:**

```bash
cd C:\Users\사용자이름\BlenderMCP
python create_test_objects.py
```

**예상 출력 (성공):**
```
============================================================
Blender MCP Connection Test
============================================================

[1/4] Creating blue cube...
✓ Connected to Blender at localhost:9876
✓ Blue cube created successfully!
```

**예상 출력 (실패):**
```
✗ Connection refused. Make sure:
  1. Blender is running
  2. MCP addon is installed and enabled
  3. Server is started (check MCP panel in Blender)
```

**실패한다면:**
- Blender가 실행 중인지 확인
- MCP addon 활성화 확인
- MCP 패널에서 "Start Server" 클릭

#### 테스트 2: MCP 서버 직접 실행

**터미널에서 MCP 서버 실행:**

```cmd
python blender_mcp_server.py
```

**서버가 정상적으로 시작되면 대기 상태가 됩니다.**

**이제 Claude Desktop을 열고 다음 메시지를 보내세요:**

```
블렌더 씬 정보를 보여줘
```

**Claude가 응답하고 터미널에 로그가 나타나야 합니다.**

---

### 6단계: 포트 충돌 확인

다른 프로그램이 포트 9876을 사용 중일 수 있습니다.

**Windows에서 포트 확인:**

```cmd
netstat -ano | findstr :9876
```

**Linux/Mac에서 포트 확인:**

```bash
lsof -i :9876
```

**포트가 사용 중이라면:**

1. 해당 프로그램 종료
2. 또는 다른 포트 사용:
   - `addon.py` 34번째 줄: `port=9876` → `port=9877` 변경
   - `claude_desktop_config.json`: `"BLENDER_PORT": "9877"` 변경
   - Blender 재시작 및 Claude Desktop 재시작

---

### 7단계: 로그 확인

#### Blender 콘솔 확인

**Windows:** `Window > Toggle System Console`

**Mac/Linux:** 터미널에서 Blender 실행

```bash
blender
```

#### Claude Desktop 로그 확인

**Windows:**
```
%APPDATA%\Claude\logs\
```

**Mac:**
```
~/Library/Logs/Claude/
```

**최신 `mcp*.log` 파일을 확인하세요.**

---

## 🔧 일반적인 문제와 해결 방법

### 문제 1: "Connection refused" 에러

**원인:**
- Blender가 실행되지 않음
- MCP addon이 비활성화됨
- MCP 서버가 시작되지 않음

**해결:**
1. Blender 실행
2. `Edit > Preferences > Add-ons`에서 "Blender MCP Server" 활성화
3. MCP 탭에서 "Start Server" 클릭

---

### 문제 2: "MCP server not found" 에러

**원인:**
- Claude Desktop 설정 파일 오류
- Python 경로 오류
- blender_mcp_server.py 경로 오류

**해결:**
1. `claude_desktop_config.json` 파일 확인
2. Python 경로가 올바른지 확인: `where python` (Windows) 또는 `which python3` (Linux/Mac)
3. blender_mcp_server.py 전체 경로 확인
4. Claude Desktop 완전 재시작

---

### 문제 3: MCP 탭이 Blender에 없음

**원인:**
- Addon이 설치되지 않음
- Addon 등록 실패
- Blender 버전 불일치

**해결:**
1. `Edit > Preferences > Add-ons` 확인
2. "MCP" 검색
3. 없으면 addon.py 재설치
4. Blender 5.0.1 이상인지 확인: `Help > About Blender`

---

### 문제 4: Addon은 있지만 서버가 시작되지 않음

**원인:**
- 포트 충돌 (다른 프로그램이 9876 포트 사용)
- 방화벽 차단
- 권한 문제

**해결:**
1. 다른 포트 사용해보기 (위 6단계 참조)
2. 방화벽에서 Python 허용
3. 관리자 권한으로 Blender 실행 (Windows)

---

### 문제 5: 서버는 실행 중이지만 명령이 실행되지 않음

**원인:**
- 잘못된 명령 형식
- Blender 메인 스레드 블로킹
- 타임아웃

**해결:**
1. Blender 콘솔에서 에러 메시지 확인
2. 간단한 명령부터 테스트: "블렌더 씬 정보를 보여줘"
3. Blender에서 무거운 작업 중이라면 완료 후 재시도

---

## 📊 체크리스트 요약

설정 전 체크리스트:

```
[ ] Blender 5.0.1 이상 설치 및 실행
[ ] addon.py 파일 Blender에 설치
[ ] MCP addon 활성화 (체크박스 체크)
[ ] MCP 탭에서 "Server Status: Running" 확인
[ ] Python 3.8 이상 설치 확인
[ ] requirements.txt 패키지 설치 (`pip install -r requirements.txt`)
[ ] Python 경로 확인 (`where python` 또는 `which python3`)
[ ] blender_mcp_server.py 파일 존재 확인
[ ] claude_desktop_config.json 올바르게 작성
[ ] 절대 경로 사용 (상대 경로 아님)
[ ] Windows 경로는 \\ 사용
[ ] JSON 문법 올바른지 확인 (괄호, 쉼표)
[ ] Claude Desktop 완전 재시작
[ ] create_test_objects.py로 연결 테스트
```

---

## 🎯 빠른 진단 스크립트

연결 상태를 자동으로 확인하려면:

```bash
python create_test_objects.py
```

성공하면 블렌더에 파란색 큐브와 노란색 구가 생성됩니다!

---

## 💬 추가 도움이 필요하면

1. **GitHub Issues 등록**
   - 에러 메시지 전체 복사
   - Blender 버전 명시
   - Python 버전 명시
   - OS 정보 명시

2. **로그 파일 첨부**
   - Blender 콘솔 출력
   - Claude Desktop 로그 (`%APPDATA%\Claude\logs\`)

3. **설정 파일 첨부**
   - `claude_desktop_config.json` 내용 (민감한 정보 제거 후)

---

## 참고: ahujasid/blender-mcp vs 이 프로젝트

| 항목 | ahujasid/blender-mcp | 이 프로젝트 |
|------|----------------------|-------------|
| 설치 방법 | `uvx blender-mcp` | `pip install -r requirements.txt` |
| Claude 설정 | `"command": "uvx"` | `"command": "python"` |
| args | `["blender-mcp"]` | `["경로/blender_mcp_server.py"]` |
| 연결 방식 | Blender에서 "Connect to Claude" 클릭 | Addon 자동 시작 |
| 패키지 매니저 | uv | pip |

**이 프로젝트는 ahujasid/blender-mcp의 포크이지만 다른 설정을 사용합니다!**

---

이 가이드로 문제가 해결되지 않으면 이슈를 등록해주세요! 🙏
