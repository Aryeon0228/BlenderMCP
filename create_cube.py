#!/usr/bin/env python3
"""
Script to create a cube in Blender via MCP socket connection
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
    print("Creating Cube in Blender")
    print("=" * 60)

    # Create a cube
    print("\nCreating cube...")
    response = send_command(HOST, PORT, "create_object", {
        "type": "cube",
        "name": "MyCube",
        "location": [0, 0, 0],
        "size": 2.0
    })

    if response and response.get("status") == "success":
        print(f"✓ Cube created successfully!")
        print(f"Result: {json.dumps(response.get('result'), indent=2)}")
    else:
        print(f"✗ Failed to create cube")
        if response:
            print(f"Response: {json.dumps(response, indent=2)}")
        return

    print("\n" + "=" * 60)
    print("✓ Done! Check your Blender viewport.")
    print("=" * 60)

if __name__ == "__main__":
    main()
