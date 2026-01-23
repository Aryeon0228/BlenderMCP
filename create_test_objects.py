#!/usr/bin/env python3
"""
Script to test Blender MCP connection and create test objects:
- Blue cube
- Yellow sphere
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
    print("Blender MCP Connection Test")
    print("=" * 60)

    # Create a blue cube
    print("\n[1/4] Creating blue cube...")
    response = send_command(HOST, PORT, "create_object", {
        "type": "cube",
        "name": "BlueCube",
        "location": [-3, 0, 0],
        "size": 2.0
    })

    if response and response.get("status") == "success":
        print(f"✓ Blue cube created successfully!")
    else:
        print(f"✗ Failed to create blue cube")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")
        return

    # Set blue color on cube
    print("\n[2/4] Setting blue color on cube...")
    response = send_command(HOST, PORT, "set_material", {
        "name": "BlueCube",
        "color": [0.0, 0.0, 1.0, 1.0]  # Blue color (R, G, B, A)
    })

    if response and response.get("status") == "success":
        print(f"✓ Blue color applied!")
    else:
        print(f"✗ Failed to set color")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")

    # Create a yellow sphere
    print("\n[3/4] Creating yellow sphere...")
    response = send_command(HOST, PORT, "create_object", {
        "type": "sphere",
        "name": "YellowSphere",
        "location": [3, 0, 0],
        "radius": 1.5
    })

    if response and response.get("status") == "success":
        print(f"✓ Yellow sphere created successfully!")
    else:
        print(f"✗ Failed to create yellow sphere")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")
        return

    # Set yellow color on sphere
    print("\n[4/4] Setting yellow color on sphere...")
    response = send_command(HOST, PORT, "set_material", {
        "name": "YellowSphere",
        "color": [1.0, 1.0, 0.0, 1.0]  # Yellow color (R, G, B, A)
    })

    if response and response.get("status") == "success":
        print(f"✓ Yellow color applied!")
    else:
        print(f"✗ Failed to set color")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")

    print("\n" + "=" * 60)
    print("✓ MCP Connection Test Complete!")
    print("✓ Check your Blender viewport for:")
    print("  - Blue cube at position (-3, 0, 0)")
    print("  - Yellow sphere at position (3, 0, 0)")
    print("=" * 60)

if __name__ == "__main__":
    main()
