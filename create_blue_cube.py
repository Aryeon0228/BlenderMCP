#!/usr/bin/env python3
"""
Script to create a blue cube in Blender via MCP socket connection
"""

import socket
import json

def send_command(host, port, command_type, params=None):
    """Send a command to Blender and get response"""
    try:
        # Connect to Blender
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        print(f"✓ Connected to Blender at {host}:{port}")

        # Prepare command
        command = {
            "type": command_type,
            "params": params or {}
        }

        # Send command
        command_json = json.dumps(command) + "\n"
        sock.sendall(command_json.encode('utf-8'))

        # Receive response
        buffer = ""
        while True:
            chunk = sock.recv(4096).decode('utf-8')
            if not chunk:
                break
            buffer += chunk
            try:
                response = json.loads(buffer)
                sock.close()
                return response
            except json.JSONDecodeError:
                continue

    except ConnectionRefusedError:
        print("✗ Connection refused. Make sure:")
        print("  1. Blender is running")
        print("  2. MCP addon is installed and enabled")
        print("  3. Server is started (check MCP panel in Blender)")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def main():
    HOST = "localhost"
    PORT = 9876

    print("=" * 60)
    print("Creating Blue Cube in Blender")
    print("=" * 60)

    # Step 1: Create a cube
    print("\n[1/2] Creating cube...")
    response = send_command(HOST, PORT, "create_object", {
        "type": "cube",
        "name": "BlueCube",
        "location": [0, 0, 0],
        "size": 2.0
    })

    if response and response.get("status") == "success":
        print(f"✓ Cube created: {response.get('result')}")
    else:
        print(f"✗ Failed to create cube: {response}")
        return

    # Step 2: Set blue material
    print("\n[2/2] Setting blue color...")
    response = send_command(HOST, PORT, "set_material", {
        "name": "BlueCube",
        "color": [0.0, 0.0, 1.0]  # RGB: Blue (0, 0, 1)
    })

    if response and response.get("status") == "success":
        print(f"✓ Blue material applied: {response.get('result')}")
    else:
        print(f"✗ Failed to set material: {response}")
        return

    print("\n" + "=" * 60)
    print("✓ Blue cube created successfully!")
    print("=" * 60)

    # Optional: Get viewport screenshot
    print("\n[Optional] Capturing viewport screenshot...")
    response = send_command(HOST, PORT, "get_viewport_screenshot", {
        "width": 1920,
        "height": 1080
    })

    if response and response.get("status") == "success":
        print("✓ Screenshot captured (base64 data available)")
        # Note: The actual image data is in response['result']['image_base64']
        # You could save it or display it if needed

if __name__ == "__main__":
    main()
