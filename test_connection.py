"""Test connection to Blender addon socket server"""
import socket
import json

try:
    print("Connecting to Blender on localhost:9876...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect(('localhost', 9876))
    print("✓ Connected!")

    # Send command
    command = {"type": "get_scene_info", "params": {}}
    command_json = json.dumps(command) + "\n"
    print(f"\nSending: {command_json.strip()}")
    s.sendall(command_json.encode('utf-8'))

    # Receive response
    print("Waiting for response...")
    buffer = ""
    while True:
        chunk = s.recv(4096).decode('utf-8')
        if not chunk:
            break
        buffer += chunk
        try:
            response = json.loads(buffer)
            print(f"\n✓ Response received:")
            print(json.dumps(response, indent=2))
            break
        except json.JSONDecodeError:
            continue

    s.close()
    print("\n✓ Connection test successful!")

except ConnectionRefusedError:
    print("✗ Connection refused - Blender addon server not running")
    print("  Check: Blender MCP addon is enabled and server is started")
except socket.timeout:
    print("✗ Connection timeout")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
