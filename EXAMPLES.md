# BlenderMCP 사용 예제

## 파란색 큐브 만들기

블렌더에 파란색 큐브를 생성하는 방법은 세 가지가 있습니다.

### 방법 1: Claude Desktop에서 MCP 도구 사용 (권장)

Blender와 MCP addon이 실행 중일 때, Claude Desktop에서 다음과 같이 요청하세요:

```
블렌더에 파란색 큐브를 만들어줘
```

또는 더 구체적으로:

```
블렌더에 (0, 0, 0) 위치에 크기가 2인 파란색 큐브를 만들고,
이름을 "BlueCube"로 설정해줘
```

### 방법 2: Python 스크립트 사용 (MCP 서버 통신)

Blender와 MCP addon이 실행 중일 때, 터미널에서:

```bash
cd BlenderMCP
python3 create_blue_cube.py
```

이 스크립트는:
1. Blender MCP 서버에 연결 (localhost:9876)
2. 큐브 생성 명령 전송
3. 파란색 재질 적용 명령 전송
4. 결과 확인

**요구사항**:
- Blender 5.0+ 실행 중
- MCP addon 설치 및 활성화
- 서버 실행 중 (MCP 패널에서 확인)

### 방법 3: Blender 내부에서 직접 실행

Blender가 설치되어 있지만 MCP addon을 설정하지 않은 경우:

1. **Blender 실행**

2. **Scripting 탭으로 이동**
   - 상단 메뉴에서 "Scripting" 클릭

3. **스크립트 열기**
   - `Text > Open Text Block` 메뉴 선택
   - `blender_create_blue_cube.py` 파일 선택

4. **스크립트 실행**
   - `Run Script` 버튼 클릭 (또는 `Alt+P`)

5. **결과 확인**
   - 뷰포트에 파란색 큐브가 생성됩니다
   - 쉐이딩 모드가 자동으로 Material Preview로 변경됩니다

## 다른 예제들

### 빨간색 구 만들기

**Claude Desktop에서**:
```
블렌더에 (2, 0, 0) 위치에 빨간색 구를 만들어줘
```

**MCP 서버 코드로**:
```python
# 구 생성
send_command(HOST, PORT, "create_object", {
    "type": "sphere",
    "name": "RedSphere",
    "location": [2, 0, 0],
    "radius": 1.0
})

# 빨간색 설정
send_command(HOST, PORT, "set_material", {
    "name": "RedSphere",
    "color": [1.0, 0.0, 0.0]  # RGB: Red
})
```

### 초록색 원기둥 만들기

**Claude Desktop에서**:
```
블렌더에 초록색 원기둥을 (-2, 0, 0)에 만들어줘
```

**Blender Python 스크립트**:
```python
import bpy

# 원기둥 생성
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    location=(-2, 0, 0)
)

cylinder = bpy.context.active_object
cylinder.name = "GreenCylinder"

# 초록색 재질
mat = bpy.data.materials.new(name="GreenMaterial")
mat.use_nodes = True
principled = mat.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)

cylinder.data.materials.append(mat)
```

### 현재 씬 정보 보기

**Claude Desktop에서**:
```
블렌더 씬 정보를 보여줘
```

**Python 스크립트**:
```python
response = send_command("localhost", 9876, "get_scene_info", {})
print(json.dumps(response, indent=2))
```

### 뷰포트 스크린샷 찍기

**Claude Desktop에서**:
```
현재 블렌더 화면을 스크린샷으로 보여줘
```

**Python 스크립트**:
```python
response = send_command("localhost", 9876, "get_viewport_screenshot", {
    "width": 1920,
    "height": 1080
})

# base64 이미지 데이터는 response['result']['image_base64']에 있습니다
```

## 색상 참고

RGB 값은 0.0 ~ 1.0 범위입니다:

| 색상 | R | G | B |
|------|---|---|---|
| 빨강 | 1.0 | 0.0 | 0.0 |
| 초록 | 0.0 | 1.0 | 0.0 |
| 파랑 | 0.0 | 0.0 | 1.0 |
| 노랑 | 1.0 | 1.0 | 0.0 |
| 청록 | 0.0 | 1.0 | 1.0 |
| 자홍 | 1.0 | 0.0 | 1.0 |
| 흰색 | 1.0 | 1.0 | 1.0 |
| 검정 | 0.0 | 0.0 | 0.0 |
| 주황 | 1.0 | 0.5 | 0.0 |
| 보라 | 0.5 | 0.0 | 1.0 |

## 문제 해결

### "Connection refused" 에러

**원인**: Blender가 실행되지 않았거나 MCP addon이 비활성화됨

**해결**:
1. Blender 실행 확인
2. Edit → Preferences → Add-ons
3. "Blender MCP Server" 검색 및 활성화
4. MCP 패널에서 "Server Status: Running" 확인

### Blender 내부 스크립트 실행 시 에러

**원인**: Blender Python API 버전 차이

**해결**:
- Blender 5.0 이상 사용
- 스크립트 콘솔에서 에러 메시지 확인
- `bpy` 모듈이 제대로 import되는지 확인

## 추가 리소스

- [Blender Python API 문서](https://docs.blender.org/api/current/)
- [MCP (Model Context Protocol) 문서](https://github.com/anthropics/mcp)
- [프로젝트 GitHub](https://github.com/Aryeon0228/BlenderMCP)
