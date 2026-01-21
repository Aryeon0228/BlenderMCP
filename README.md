# BlenderMCP - Blender Model Context Protocol Integration

> 🇰🇷 **한글 설명**
> BlenderMCP는 Claude AI와 Blender를 연결하여 AI가 Blender를 직접 제어할 수 있게 해주는 통합 도구입니다.
> 프롬프트를 통해 3D 모델링, 씬 생성, 객체 조작을 AI와 함께 할 수 있습니다.

BlenderMCP connects Blender to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Blender. This integration enables prompt assisted 3D modeling, scene creation, and manipulation.

**We have no official website. Any website you see online is unofficial and has no affiliation with this project. Use them at your own risk.**

[Full tutorial](https://www.youtube.com/watch?v=lCyQ717DuzQ)

### Join the Community

Give feedback, get inspired, and build on top of the MCP: [Discord](https://discord.gg/z5apgR8TFU)

### Supporters

[CodeRabbit](https://www.coderabbit.ai/)

**All supporters:**

[Support this project](https://github.com/sponsors/ahujasid)

## Release notes (1.4.0)
- Added Hunyuan3D support


### Previously added features:
- View screenshots for Blender viewport to better understand the scene
- Search and download Sketchfab models
- Support for Poly Haven assets through their API
- Support to generate 3D models using Hyper3D Rodin
- Run Blender MCP on a remote host
- Telemetry for tools executed (completely anonymous)

### Installating a new version (existing users)
- For newcomers, you can go straight to Installation. For existing users, see the points below
- Download the latest addon.py file and replace the older one, then add it to Blender
- Delete the MCP server from Claude and add it back again, and you should be good to go!


## Features

> 🇰🇷 **주요 기능**
> - **양방향 통신**: 소켓 기반 서버로 Claude AI와 Blender 연결
> - **객체 조작**: Blender에서 3D 객체 생성, 수정, 삭제
> - **머티리얼 제어**: 재질과 색상 적용 및 수정
> - **씬 검사**: 현재 Blender 씬의 상세 정보 확인
> - **코드 실행**: Claude에서 Blender Python 코드 실행

- **Two-way communication**: Connect Claude AI to Blender through a socket-based server
- **Object manipulation**: Create, modify, and delete 3D objects in Blender
- **Material control**: Apply and modify materials and colors
- **Scene inspection**: Get detailed information about the current Blender scene
- **Code execution**: Run arbitrary Python code in Blender from Claude

## Components

The system consists of two main components:

1. **Blender Addon (`addon.py`)**: A Blender addon that creates a socket server within Blender to receive and execute commands
2. **MCP Server (`src/blender_mcp/server.py`)**: A Python server that implements the Model Context Protocol and connects to the Blender addon

## Installation

> 🇰🇷 **설치 방법**
>
> ### 필수 요구사항
> - Blender 3.0 이상
> - Python 3.10 이상
> - uv 패키지 매니저
>
> ### uv 설치
> **Mac:**
> ```bash
> brew install uv
> ```
>
> **Windows:**
> ```powershell
> powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
> ```
> 그 후 환경 변수에 uv를 추가하세요:
> ```powershell
> $localBin = "$env:USERPROFILE\.local\bin"
> $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
> [Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
> ```


### Prerequisites

- Blender 3.0 or newer
- Python 3.10 or newer
- uv package manager:

**If you're on Mac, please install uv as**
```bash
brew install uv
```
**On Windows**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
and then add uv to the user path in Windows (you may need to restart Claude Desktop after):
```powershell
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

Otherwise installation instructions are on their website: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

**⚠️ Do not proceed before installing UV**

### Environment Variables

The following environment variables can be used to configure the Blender connection:

- `BLENDER_HOST`: Host address for Blender socket server (default: "localhost")
- `BLENDER_PORT`: Port number for Blender socket server (default: 9876)

Example:
```bash
export BLENDER_HOST='host.docker.internal'
export BLENDER_PORT=9876
```

### Claude for Desktop Integration

> 🇰🇷 **Claude Desktop 연동**
>
> Claude > 설정 > 개발자 > 설정 편집 > claude_desktop_config.json 에서 다음을 추가:

[Watch the setup instruction video](https://www.youtube.com/watch?v=neoK_WMq92g) (Assuming you have already installed uv)

Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```
<details>
<summary>Claude Code</summary>

Use the Claude Code CLI to add the blender MCP server:

```bash
claude mcp add blender uvx blender-mcp
```
</details>

### Cursor integration

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=blender&config=eyJjb21tYW5kIjoidXZ4IGJsZW5kZXItbWNwIn0%3D)

For Mac users, go to Settings > MCP and paste the following

- To use as a global server, use "add new global MCP server" button and paste
- To use as a project specific server, create `.cursor/mcp.json` in the root of the project and paste


```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```

For Windows users, go to Settings > MCP > Add Server, add a new server with the following settings:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "blender-mcp"
            ]
        }
    }
}
```

[Cursor setup video](https://www.youtube.com/watch?v=wgWsJshecac)

**⚠️ Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both**

### Visual Studio Code Integration

_Prerequisites_: Make sure you have [Visual Studio Code](https://code.visualstudio.com/) installed before proceeding.

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_blender--mcp_server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22blender-mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22blender-mcp%22%5D%7D)

### Installing the Blender Addon

> 🇰🇷 **Blender 애드온 설치**
>
> 1. 이 저장소에서 `addon.py` 파일 다운로드
> 2. Blender 열기
> 3. 편집 > 환경설정 > 애드온으로 이동
> 4. "설치..." 클릭 후 `addon.py` 파일 선택
> 5. "Interface: Blender MCP" 옆의 체크박스를 활성화

1. Download the `addon.py` file from this repo
1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install..." and select the `addon.py` file
4. Enable the addon by checking the box next to "Interface: Blender MCP"


## Usage

> 🇰🇷 **사용 방법**
>
> ### 연결 시작하기
> 1. Blender에서 3D 뷰 사이드바 열기 (N 키)
> 2. "BlenderMCP" 탭 찾기
> 3. Poly Haven 에셋을 사용하려면 체크박스 켜기 (선택사항)
> 4. "Connect to Claude" 클릭
> 5. 터미널에서 MCP 서버가 실행 중인지 확인

### Starting the Connection
![BlenderMCP in the sidebar](assets/addon-instructions.png)

1. In Blender, go to the 3D View sidebar (press N if not visible)
2. Find the "BlenderMCP" tab
3. Turn on the Poly Haven checkbox if you want assets from their API (optional)
4. Click "Connect to Claude"
5. Make sure the MCP server is running in your terminal

### Using with Claude

Once the config file has been set on Claude, and the addon is running on Blender, you will see a hammer icon with tools for the Blender MCP.

![BlenderMCP in the sidebar](assets/hammer-icon.png)

#### Capabilities

- Get scene and object information
- Create, delete and modify shapes
- Apply or create materials for objects
- Execute any Python code in Blender
- Download the right models, assets and HDRIs through [Poly Haven](https://polyhaven.com/)
- AI generated 3D models through [Hyper3D Rodin](https://hyper3d.ai/)


### Example Commands

> 🇰🇷 **예시 명령어**
> - "던전 안에 용이 금 항아리를 지키고 있는 로우 폴리 씬을 만들어줘"
> - "Poly Haven에서 HDRI, 텍스처, 바위와 식물 모델을 사용해서 해변 분위기를 만들어줘"
> - "이 차를 빨간색과 금속 재질로 만들어줘"
> - "구체를 만들고 큐브 위에 배치해줘"

Here are some examples of what you can ask Claude to do:

- "Create a low poly scene in a dungeon, with a dragon guarding a pot of gold" [Demo](https://www.youtube.com/watch?v=DqgKuLYUv00)
- "Create a beach vibe using HDRIs, textures, and models like rocks and vegetation from Poly Haven" [Demo](https://www.youtube.com/watch?v=I29rn92gkC4)
- Give a reference image, and create a Blender scene out of it [Demo](https://www.youtube.com/watch?v=FDRb03XPiRo)
- "Generate a 3D model of a garden gnome through Hyper3D"
- "Get information about the current scene, and make a threejs sketch from it" [Demo](https://www.youtube.com/watch?v=jxbNI5L7AH8)
- "Make this car red and metallic"
- "Create a sphere and place it above the cube"
- "Make the lighting like a studio"
- "Point the camera at the scene, and make it isometric"

## Hyper3D integration

Hyper3D's free trial key allows you to generate a limited number of models per day. If the daily limit is reached, you can wait for the next day's reset or obtain your own key from hyper3d.ai and fal.ai.

## Troubleshooting

> 🇰🇷 **문제 해결**
> - **연결 문제**: Blender 애드온 서버가 실행 중이고 MCP 서버가 Claude에 설정되어 있는지 확인하세요. 터미널에서 uvx 명령을 직접 실행하지 마세요.
> - **타임아웃 에러**: 요청을 단순화하거나 더 작은 단계로 나누세요.
> - **켜고 끄기**: 여전히 연결 오류가 있다면 Claude와 Blender 서버를 모두 재시작해보세요.

- **Connection issues**: Make sure the Blender addon server is running, and the MCP server is configured on Claude, DO NOT run the uvx command in the terminal. Sometimes, the first command won't go through but after that it starts working.
- **Timeout errors**: Try simplifying your requests or breaking them into smaller steps
- **Poly Haven integration**: Claude is sometimes erratic with its behaviour
- **Have you tried turning it off and on again?**: If you're still having connection errors, try restarting both Claude and the Blender server


## Technical Details

### Communication Protocol

The system uses a simple JSON-based protocol over TCP sockets:

- **Commands** are sent as JSON objects with a `type` and optional `params`
- **Responses** are JSON objects with a `status` and `result` or `message`

## Limitations & Security Considerations

> 🇰🇷 **제한사항 및 보안 고려사항**
> - `execute_blender_code` 도구는 Blender에서 임의의 Python 코드를 실행할 수 있습니다. 사용 전에 항상 작업을 저장하세요.
> - Poly Haven은 모델, 텍스처, HDRI 이미지를 다운로드합니다. 사용하지 않으려면 Blender 체크박스에서 끄세요.
> - 복잡한 작업은 더 작은 단계로 나눠야 할 수 있습니다.

- The `execute_blender_code` tool allows running arbitrary Python code in Blender, which can be powerful but potentially dangerous. Use with caution in production environments. ALWAYS save your work before using it.
- Poly Haven requires downloading models, textures, and HDRI images. If you do not want to use it, please turn it off in the checkbox in Blender.
- Complex operations might need to be broken down into smaller steps


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This is a third-party integration and not made by Blender. Made by [Siddharth](https://x.com/sidahuj)

---

## 🇰🇷 한국어 빠른 시작 가이드

### 1. 사전 준비
- Blender 3.0 이상 설치
- Python 3.10 이상 설치
- uv 패키지 매니저 설치 (위 설치 방법 참조)

### 2. MCP 서버 설정
Claude Desktop의 설정 파일(`claude_desktop_config.json`)에 다음을 추가:
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

### 3. Blender 애드온 설치
1. `addon.py` 다운로드
2. Blender > 편집 > 환경설정 > 애드온
3. "설치..." 버튼 클릭 후 `addon.py` 선택
4. "Interface: Blender MCP" 활성화

### 4. 사용하기
1. Blender에서 N 키를 눌러 사이드바 열기
2. "BlenderMCP" 탭에서 "Connect to Claude" 클릭
3. Claude Desktop에서 Blender 관련 프롬프트 입력
4. AI가 자동으로 3D 모델링 수행!

### 5. 예시
```
"빨간색 구체와 파란색 큐브를 만들어줘"
"스튜디오 조명을 설정해줘"
"카메라를 씬을 향하게 하고 아이소메트릭으로 만들어줘"
```
