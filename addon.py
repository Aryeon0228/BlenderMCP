"""
Blender MCP Server Addon
A Blender addon that creates a socket server to receive and execute commands from Claude Desktop
"""

bl_info = {
    "name": "Blender MCP Server",
    "author": "BlenderMCP",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Socket server for controlling Blender via Model Context Protocol",
    "category": "Development",
}

import bpy
import socket
import json
import threading
import traceback
import base64
import tempfile
import os
from mathutils import Vector


# Global server instance
_server_instance = None


class BlenderMCPServer:
    """Socket server running inside Blender to handle MCP commands"""

    def __init__(self, host="localhost", port=9876):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None

        # Command handlers
        self.handlers = {
            "get_scene_info": self._handle_get_scene_info,
            "get_object_info": self._handle_get_object_info,
            "create_object": self._handle_create_object,
            "delete_object": self._handle_delete_object,
            "move_object": self._handle_move_object,
            "scale_object": self._handle_scale_object,
            "rotate_object": self._handle_rotate_object,
            "execute_code": self._handle_execute_code,
            "get_viewport_screenshot": self._handle_get_viewport_screenshot,
            "set_material": self._handle_set_material,
            "render_scene": self._handle_render_scene,
            "save_file": self._handle_save_file,
        }

    def start(self):
        """Start the socket server"""
        if self.running:
            print("Server already running")
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)
            self.running = True

            print(f"Blender MCP Server started on {self.host}:{self.port}")

            # Start server loop in daemon thread
            self.thread = threading.Thread(target=self._server_loop, daemon=True)
            self.thread.start()

        except Exception as e:
            print(f"Failed to start server: {e}")
            self.running = False

    def stop(self):
        """Stop the socket server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("Blender MCP Server stopped")

    def _server_loop(self):
        """Main server loop accepting connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Client connected from {addr}")

                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")

    def _handle_client(self, client_socket):
        """Handle individual client connection"""
        buffer = ""
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                # Try to parse complete JSON commands
                while buffer:
                    try:
                        command, idx = json.JSONDecoder().raw_decode(buffer)
                        buffer = buffer[idx:].lstrip()

                        # Process command
                        response = self._process_command(command)

                        # Send response
                        response_json = json.dumps(response) + "\n"
                        client_socket.sendall(response_json.encode('utf-8'))

                    except json.JSONDecodeError:
                        # Incomplete JSON, wait for more data
                        break

        except Exception as e:
            print(f"Client handler error: {e}")
            traceback.print_exc()
        finally:
            client_socket.close()

    def _process_command(self, command):
        """Process a command and return response"""
        try:
            cmd_type = command.get("type")
            params = command.get("params", {})

            if cmd_type not in self.handlers:
                return {
                    "status": "error",
                    "message": f"Unknown command: {cmd_type}"
                }

            # Execute handler in main thread
            result = {"status": "pending"}
            result_container = [result]

            def execute_in_main_thread():
                try:
                    handler = self.handlers[cmd_type]
                    result_container[0] = handler(params)
                except Exception as e:
                    result_container[0] = {
                        "status": "error",
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }

            # Schedule execution in Blender's main thread
            bpy.app.timers.register(execute_in_main_thread, first_interval=0.0)

            # Wait for execution (with timeout)
            import time
            timeout = 180
            start_time = time.time()
            while result_container[0]["status"] == "pending":
                time.sleep(0.1)
                if time.time() - start_time > timeout:
                    return {
                        "status": "error",
                        "message": "Command execution timeout"
                    }

            return result_container[0]

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    # Command Handlers

    def _handle_get_scene_info(self, params):
        """Get information about the current scene"""
        scene = bpy.context.scene

        objects = []
        for obj in scene.objects:
            objects.append({
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale),
                "visible": not obj.hide_get(),
            })

        return {
            "status": "success",
            "result": {
                "name": scene.name,
                "frame_current": scene.frame_current,
                "frame_start": scene.frame_start,
                "frame_end": scene.frame_end,
                "render_engine": scene.render.engine,
                "objects": objects,
                "object_count": len(objects),
            }
        }

    def _handle_get_object_info(self, params):
        """Get detailed information about a specific object"""
        obj_name = params.get("name")
        if not obj_name:
            return {"status": "error", "message": "Object name required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        info = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation_euler": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "dimensions": list(obj.dimensions),
            "visible": not obj.hide_get(),
        }

        # Add mesh-specific info
        if obj.type == 'MESH' and obj.data:
            info["vertices"] = len(obj.data.vertices)
            info["edges"] = len(obj.data.edges)
            info["faces"] = len(obj.data.polygons)

        return {"status": "success", "result": info}

    def _handle_create_object(self, params):
        """Create a new object"""
        obj_type = params.get("type", "cube").lower()
        name = params.get("name")
        location = params.get("location", [0, 0, 0])

        # Create object based on type
        if obj_type == "cube":
            bpy.ops.mesh.primitive_cube_add(size=params.get("size", 2.0), location=location)
        elif obj_type == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=params.get("radius", 1.0),
                location=location,
                segments=params.get("segments", 32),
                ring_count=params.get("ring_count", 16)
            )
        elif obj_type == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(
                radius=params.get("radius", 1.0),
                depth=params.get("depth", 2.0),
                location=location
            )
        elif obj_type == "cone":
            bpy.ops.mesh.primitive_cone_add(
                radius1=params.get("radius", 1.0),
                depth=params.get("depth", 2.0),
                location=location
            )
        elif obj_type == "plane":
            bpy.ops.mesh.primitive_plane_add(
                size=params.get("size", 2.0),
                location=location
            )
        elif obj_type == "torus":
            bpy.ops.mesh.primitive_torus_add(
                major_radius=params.get("major_radius", 1.0),
                minor_radius=params.get("minor_radius", 0.25),
                location=location
            )
        else:
            return {"status": "error", "message": f"Unknown object type: {obj_type}"}

        # Get the created object
        obj = bpy.context.active_object

        # Rename if name provided
        if name:
            obj.name = name

        return {
            "status": "success",
            "result": {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location)
            }
        }

    def _handle_delete_object(self, params):
        """Delete an object"""
        obj_name = params.get("name")
        if not obj_name:
            return {"status": "error", "message": "Object name required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        bpy.data.objects.remove(obj, do_unlink=True)

        return {"status": "success", "result": {"deleted": obj_name}}

    def _handle_move_object(self, params):
        """Move an object"""
        obj_name = params.get("name")
        location = params.get("location")

        if not obj_name or location is None:
            return {"status": "error", "message": "Object name and location required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        obj.location = Vector(location)

        return {
            "status": "success",
            "result": {"name": obj_name, "location": list(obj.location)}
        }

    def _handle_scale_object(self, params):
        """Scale an object"""
        obj_name = params.get("name")
        scale = params.get("scale")

        if not obj_name or scale is None:
            return {"status": "error", "message": "Object name and scale required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        if isinstance(scale, (int, float)):
            obj.scale = Vector([scale, scale, scale])
        else:
            obj.scale = Vector(scale)

        return {
            "status": "success",
            "result": {"name": obj_name, "scale": list(obj.scale)}
        }

    def _handle_rotate_object(self, params):
        """Rotate an object"""
        obj_name = params.get("name")
        rotation = params.get("rotation")

        if not obj_name or rotation is None:
            return {"status": "error", "message": "Object name and rotation required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        obj.rotation_euler = Vector(rotation)

        return {
            "status": "success",
            "result": {"name": obj_name, "rotation": list(obj.rotation_euler)}
        }

    def _handle_execute_code(self, params):
        """Execute arbitrary Python code"""
        code = params.get("code")
        if not code:
            return {"status": "error", "message": "Code required"}

        try:
            # Create a namespace for execution
            namespace = {
                "bpy": bpy,
                "C": bpy.context,
                "D": bpy.data,
            }

            # Execute code
            exec(code, namespace)

            # Capture any output
            result = namespace.get("result", "Code executed successfully")

            return {
                "status": "success",
                "result": str(result)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }

    def _handle_get_viewport_screenshot(self, params):
        """Capture viewport screenshot"""
        width = params.get("width", 1920)
        height = params.get("height", 1080)

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Set render settings
            scene = bpy.context.scene
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.filepath = tmp_path

            # Render viewport
            bpy.ops.render.opengl(write_still=True)

            # Read image and encode as base64
            with open(tmp_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            return {
                "status": "success",
                "result": {
                    "image_base64": image_data,
                    "width": width,
                    "height": height
                }
            }
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _handle_set_material(self, params):
        """Set material properties for an object"""
        obj_name = params.get("name")
        color = params.get("color")

        if not obj_name:
            return {"status": "error", "message": "Object name required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "message": f"Object '{obj_name}' not found"}

        # Create or get material
        mat_name = f"{obj_name}_Material"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True

        # Set color if provided
        if color:
            nodes = mat.node_tree.nodes
            principled = nodes.get("Principled BSDF")
            if principled:
                principled.inputs["Base Color"].default_value = tuple(color) + (1.0,) if len(color) == 3 else tuple(color)

        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        return {
            "status": "success",
            "result": {"object": obj_name, "material": mat_name}
        }

    def _handle_render_scene(self, params):
        """Render the scene"""
        output_path = params.get("output_path")
        if not output_path:
            return {"status": "error", "message": "Output path required"}

        scene = bpy.context.scene
        scene.render.filepath = output_path

        # Set render settings if provided
        if "resolution_x" in params:
            scene.render.resolution_x = params["resolution_x"]
        if "resolution_y" in params:
            scene.render.resolution_y = params["resolution_y"]
        if "samples" in params and hasattr(scene, "cycles"):
            scene.cycles.samples = params["samples"]

        # Render
        bpy.ops.render.render(write_still=True)

        return {
            "status": "success",
            "result": {"output": output_path}
        }

    def _handle_save_file(self, params):
        """Save the blend file"""
        filepath = params.get("filepath")
        if not filepath:
            return {"status": "error", "message": "Filepath required"}

        bpy.ops.wm.save_as_mainfile(filepath=filepath)

        return {
            "status": "success",
            "result": {"saved": filepath}
        }


# Blender UI Panel

class BLENDERMCP_PT_MainPanel(bpy.types.Panel):
    """Main panel for Blender MCP Server"""
    bl_label = "Blender MCP Server"
    bl_idname = "BLENDERMCP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MCP'

    def draw(self, context):
        layout = self.layout

        global _server_instance

        if _server_instance and _server_instance.running:
            layout.label(text="Server Status: Running", icon='PLAY')
            layout.label(text=f"Port: {_server_instance.port}")
            layout.operator("blendermcp.stop_server", icon='PAUSE')
        else:
            layout.label(text="Server Status: Stopped", icon='PAUSE')
            layout.operator("blendermcp.start_server", icon='PLAY')


class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    """Start the MCP Server"""
    bl_idname = "blendermcp.start_server"
    bl_label = "Start Server"

    def execute(self, context):
        global _server_instance

        if not _server_instance:
            _server_instance = BlenderMCPServer()

        _server_instance.start()
        self.report({'INFO'}, "MCP Server started")
        return {'FINISHED'}


class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    """Stop the MCP Server"""
    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop Server"

    def execute(self, context):
        global _server_instance

        if _server_instance:
            _server_instance.stop()

        self.report({'INFO'}, "MCP Server stopped")
        return {'FINISHED'}


# Registration

classes = (
    BLENDERMCP_PT_MainPanel,
    BLENDERMCP_OT_StartServer,
    BLENDERMCP_OT_StopServer,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Auto-start server
    global _server_instance
    if not _server_instance:
        _server_instance = BlenderMCPServer()
        _server_instance.start()


def unregister():
    global _server_instance

    # Stop server
    if _server_instance:
        _server_instance.stop()
        _server_instance = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
