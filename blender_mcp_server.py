#!/usr/bin/env python3
"""
Blender MCP Server
A Model Context Protocol server that connects to Blender via socket communication
"""

import asyncio
import json
import os
import socket
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Configuration
BLENDER_HOST = os.environ.get("BLENDER_HOST", "localhost")
BLENDER_PORT = int(os.environ.get("BLENDER_PORT", "9876"))

# Initialize MCP server
server = Server("blender-mcp")

# Global connection
_blender_connection = None


class BlenderConnection:
    """Manages socket connection to Blender addon"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Establish connection to Blender"""
        if self.socket:
            return  # Already connected

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(180)  # 3 minute timeout
            self.socket.connect((self.host, self.port))
            print(f"Connected to Blender at {self.host}:{self.port}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Blender: {e}. Make sure Blender is running with the MCP addon enabled.")

    def disconnect(self):
        """Close connection"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def send_command(self, command_type: str, params: dict = None) -> dict:
        """Send command to Blender and get response"""
        if not self.socket:
            self.connect()

        command = {
            "type": command_type,
            "params": params or {}
        }

        try:
            # Send command
            command_json = json.dumps(command) + "\n"
            self.socket.sendall(command_json.encode('utf-8'))

            # Receive response (with chunking support for large responses)
            buffer = ""
            while True:
                chunk = self.socket.recv(4096).decode('utf-8')
                if not chunk:
                    raise ConnectionError("Connection closed by Blender")

                buffer += chunk

                # Try to parse complete JSON
                try:
                    response = json.loads(buffer)
                    return response
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving
                    continue

        except Exception as e:
            # Connection error, reset socket
            self.disconnect()
            raise ConnectionError(f"Communication error: {e}")


def get_connection() -> BlenderConnection:
    """Get or create Blender connection"""
    global _blender_connection
    if not _blender_connection:
        _blender_connection = BlenderConnection(BLENDER_HOST, BLENDER_PORT)
    return _blender_connection


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Blender control tools"""
    return [
        Tool(
            name="get_scene_info",
            description="Get information about the current Blender scene including all objects, frame range, and render settings",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_object_info",
            description="Get detailed information about a specific object in the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object to query"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="create_object",
            description="Create a new 3D object in Blender. Supports: cube, sphere, cylinder, cone, plane, torus",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Type of object: cube, sphere, cylinder, cone, plane, torus",
                        "enum": ["cube", "sphere", "cylinder", "cone", "plane", "torus"]
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional name for the object"
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Position [x, y, z]",
                        "default": [0, 0, 0]
                    },
                    "size": {
                        "type": "number",
                        "description": "Size (for cube, plane)"
                    },
                    "radius": {
                        "type": "number",
                        "description": "Radius (for sphere, cylinder, cone)"
                    },
                    "depth": {
                        "type": "number",
                        "description": "Depth/height (for cylinder, cone)"
                    }
                },
                "required": ["type"]
            }
        ),
        Tool(
            name="delete_object",
            description="Delete an object from the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object to delete"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="move_object",
            description="Move an object to a new location",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object"
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "New position [x, y, z]"
                    }
                },
                "required": ["name", "location"]
            }
        ),
        Tool(
            name="scale_object",
            description="Scale an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object"
                    },
                    "scale": {
                        "description": "Scale factor (number for uniform, or [x,y,z] for non-uniform)",
                    }
                },
                "required": ["name", "scale"]
            }
        ),
        Tool(
            name="rotate_object",
            description="Rotate an object (Euler angles in radians)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object"
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Rotation [x, y, z] in radians"
                    }
                },
                "required": ["name", "rotation"]
            }
        ),
        Tool(
            name="execute_blender_code",
            description="Execute arbitrary Python code in Blender context. Has access to bpy, C (context), D (data). WARNING: This can modify or delete your scene. Save your work first!",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute in Blender"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="get_viewport_screenshot",
            description="Capture a screenshot of the current viewport",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "Screenshot width in pixels",
                        "default": 1920
                    },
                    "height": {
                        "type": "integer",
                        "description": "Screenshot height in pixels",
                        "default": 1080
                    }
                }
            }
        ),
        Tool(
            name="set_material",
            description="Set material properties for an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the object"
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "RGB or RGBA color values [r, g, b] or [r, g, b, a] (0-1 range)"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="render_scene",
            description="Render the current scene to an image file",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Output file path (absolute path recommended)"
                    },
                    "resolution_x": {
                        "type": "integer",
                        "description": "Render width",
                        "default": 1920
                    },
                    "resolution_y": {
                        "type": "integer",
                        "description": "Render height",
                        "default": 1080
                    },
                    "samples": {
                        "type": "integer",
                        "description": "Render samples (for Cycles)",
                        "default": 128
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="save_blend_file",
            description="Save the current Blender scene to a .blend file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path where to save the .blend file"
                    }
                },
                "required": ["filepath"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls by sending commands to Blender"""

    try:
        conn = get_connection()

        # Map MCP tool names to Blender command types
        command_mapping = {
            "get_scene_info": "get_scene_info",
            "get_object_info": "get_object_info",
            "create_object": "create_object",
            "delete_object": "delete_object",
            "move_object": "move_object",
            "scale_object": "scale_object",
            "rotate_object": "rotate_object",
            "execute_blender_code": "execute_code",
            "get_viewport_screenshot": "get_viewport_screenshot",
            "set_material": "set_material",
            "render_scene": "render_scene",
            "save_blend_file": "save_file",
        }

        command_type = command_mapping.get(name)
        if not command_type:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

        # Send command to Blender
        response = conn.send_command(command_type, arguments)

        # Handle response
        if response.get("status") == "success":
            result = response.get("result", {})

            # Special handling for screenshots
            if name == "get_viewport_screenshot" and "image_base64" in result:
                import base64
                image_data = base64.b64decode(result["image_base64"])
                return [
                    ImageContent(
                        type="image",
                        data=image_data,
                        mimeType="image/png"
                    ),
                    TextContent(
                        type="text",
                        text=f"Screenshot captured: {result.get('width')}x{result.get('height')}"
                    )
                ]

            # Standard text response
            if isinstance(result, dict):
                result_text = json.dumps(result, indent=2)
            else:
                result_text = str(result)

            return [TextContent(
                type="text",
                text=f"✓ Success:\n{result_text}"
            )]

        else:
            # Error response
            error_msg = response.get("message", "Unknown error")
            traceback_info = response.get("traceback", "")

            error_text = f"✗ Error: {error_msg}"
            if traceback_info:
                error_text += f"\n\nTraceback:\n{traceback_info}"

            return [TextContent(
                type="text",
                text=error_text
            )]

    except ConnectionError as e:
        return [TextContent(
            type="text",
            text=f"✗ Connection Error: {e}\n\nMake sure:\n1. Blender is running\n2. The MCP addon is installed and enabled\n3. The server is started (check the MCP panel in Blender)"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"✗ Unexpected error: {e}"
        )]


async def main():
    """Main entry point"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
