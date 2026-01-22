#!/usr/bin/env python3
"""
Blender MCP Server
A Model Context Protocol server for controlling Blender 5.0.1
"""

import asyncio
import sys
import subprocess
import os
from typing import Any, Sequence
import json

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl


# Blender executable path - will be configured based on Windows installation
BLENDER_PATH = os.environ.get("BLENDER_PATH", "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe")

# Initialize MCP server
server = Server("blender-mcp")


async def run_blender_script(script: str, background: bool = True) -> dict[str, Any]:
    """
    Execute a Python script in Blender.

    Args:
        script: Python script to execute in Blender
        background: Run Blender in background mode

    Returns:
        Dictionary with stdout, stderr, and return code
    """
    # Create temporary script file
    import tempfile
    import time

    # Use tempfile to avoid conflicts
    fd, script_file = tempfile.mkstemp(suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(script)
    except:
        os.close(fd)
        raise

    try:
        # Build command
        cmd = [BLENDER_PATH]
        if background:
            cmd.append("--background")
        cmd.extend(["--python", script_file])

        # Run Blender synchronously in thread pool to avoid Windows asyncio issues
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,  # 2 minute timeout
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
        )

        return {
            "stdout": result.stdout.decode("utf-8", errors="ignore"),
            "stderr": result.stderr.decode("utf-8", errors="ignore"),
            "returncode": result.returncode,
            "success": result.returncode == 0
        }
    finally:
        # Clean up temp file
        try:
            if os.path.exists(script_file):
                os.remove(script_file)
        except:
            pass


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Blender control tools."""
    return [
        Tool(
            name="create_cube",
            description="Create a cube in the Blender scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the cube object",
                        "default": "Cube"
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Location [x, y, z] in 3D space",
                        "default": [0, 0, 0]
                    },
                    "size": {
                        "type": "number",
                        "description": "Size of the cube",
                        "default": 2.0
                    }
                }
            }
        ),
        Tool(
            name="create_sphere",
            description="Create a UV sphere in the Blender scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the sphere object",
                        "default": "Sphere"
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Location [x, y, z] in 3D space",
                        "default": [0, 0, 0]
                    },
                    "radius": {
                        "type": "number",
                        "description": "Radius of the sphere",
                        "default": 1.0
                    },
                    "subdivisions": {
                        "type": "integer",
                        "description": "Number of subdivisions",
                        "default": 32
                    }
                }
            }
        ),
        Tool(
            name="execute_python",
            description="Execute arbitrary Python code in Blender context",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute in Blender"
                    },
                    "background": {
                        "type": "boolean",
                        "description": "Run in background mode (no GUI)",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="render_scene",
            description="Render the current Blender scene to an image",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Output file path for the rendered image"
                    },
                    "resolution_x": {
                        "type": "integer",
                        "description": "Render resolution width",
                        "default": 1920
                    },
                    "resolution_y": {
                        "type": "integer",
                        "description": "Render resolution height",
                        "default": 1080
                    },
                    "samples": {
                        "type": "integer",
                        "description": "Number of render samples",
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
        Tool(
            name="get_blender_info",
            description="Get information about Blender installation and version",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_objects",
            description="List all objects in the current Blender scene",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="delete_object",
            description="Delete an object from the Blender scene by name",
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
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for Blender operations."""

    if name == "create_cube":
        cube_name = arguments.get("name", "Cube")
        location = arguments.get("location", [0, 0, 0])
        size = arguments.get("size", 2.0)

        script = f"""
import bpy

# Create cube
bpy.ops.mesh.primitive_cube_add(size={size}, location=({location[0]}, {location[1]}, {location[2]}))
cube = bpy.context.active_object
cube.name = "{cube_name}"

print(f"Created cube '{{cube.name}}' at location {location}")
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"✓ Created cube '{cube_name}' at location {location} with size {size}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to create cube:\n{result['stderr']}"
            )]

    elif name == "create_sphere":
        sphere_name = arguments.get("name", "Sphere")
        location = arguments.get("location", [0, 0, 0])
        radius = arguments.get("radius", 1.0)
        subdivisions = arguments.get("subdivisions", 32)

        script = f"""
import bpy

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius={radius},
    location=({location[0]}, {location[1]}, {location[2]}),
    segments={subdivisions},
    ring_count={subdivisions//2}
)
sphere = bpy.context.active_object
sphere.name = "{sphere_name}"

print(f"Created sphere '{{sphere.name}}' at location {location}")
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"✓ Created sphere '{sphere_name}' at location {location} with radius {radius}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to create sphere:\n{result['stderr']}"
            )]

    elif name == "execute_python":
        code = arguments.get("code", "")
        background = arguments.get("background", True)

        result = await run_blender_script(code, background=background)

        return [TextContent(
            type="text",
            text=f"Execution {'succeeded' if result['success'] else 'failed'}:\n\nOutput:\n{result['stdout']}\n\nErrors:\n{result['stderr']}"
        )]

    elif name == "render_scene":
        output_path = arguments.get("output_path")
        resolution_x = arguments.get("resolution_x", 1920)
        resolution_y = arguments.get("resolution_y", 1080)
        samples = arguments.get("samples", 128)

        # Convert to absolute path for Windows
        output_path = os.path.abspath(output_path)

        script = f"""
import bpy

# Set render settings
scene = bpy.context.scene
scene.render.resolution_x = {resolution_x}
scene.render.resolution_y = {resolution_y}
scene.render.filepath = r"{output_path}"

# Set cycles render engine if available
if hasattr(bpy.context.scene, 'cycles'):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = {samples}

# Render
bpy.ops.render.render(write_still=True)
print(f"Rendered to: {output_path}")
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"✓ Rendered scene to: {output_path}\nResolution: {resolution_x}x{resolution_y}, Samples: {samples}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to render:\n{result['stderr']}"
            )]

    elif name == "save_blend_file":
        filepath = arguments.get("filepath")
        filepath = os.path.abspath(filepath)

        script = f"""
import bpy

bpy.ops.wm.save_as_mainfile(filepath=r"{filepath}")
print(f"Saved to: {filepath}")
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"✓ Saved Blender file to: {filepath}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to save file:\n{result['stderr']}"
            )]

    elif name == "get_blender_info":
        script = """
import bpy
import sys

info = {
    'version': bpy.app.version_string,
    'build_date': bpy.app.build_date.decode('utf-8'),
    'python_version': sys.version,
    'executable': bpy.app.binary_path
}

import json
print(json.dumps(info, indent=2))
"""
        result = await run_blender_script(script)

        return [TextContent(
            type="text",
            text=f"Blender Information:\n{result['stdout']}"
        )]

    elif name == "list_objects":
        script = """
import bpy
import json

objects = []
for obj in bpy.data.objects:
    objects.append({
        'name': obj.name,
        'type': obj.type,
        'location': list(obj.location)
    })

print(json.dumps(objects, indent=2))
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Objects in scene:\n{result['stdout']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to list objects:\n{result['stderr']}"
            )]

    elif name == "delete_object":
        obj_name = arguments.get("name")

        script = f"""
import bpy

obj = bpy.data.objects.get("{obj_name}")
if obj:
    bpy.data.objects.remove(obj, do_unlink=True)
    print(f"Deleted object: {obj_name}")
else:
    print(f"Object not found: {obj_name}")
    import sys
    sys.exit(1)
"""
        result = await run_blender_script(script)

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"✓ Deleted object: {obj_name}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"✗ Failed to delete object:\n{result['stderr']}"
            )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Main entry point for the server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
