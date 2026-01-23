#!/usr/bin/env python3
"""
Direct test of MCP server by simulating what Claude Desktop does
"""
import json
import subprocess
import sys

# Start MCP server
print("Starting MCP server...")
process = subprocess.Popen(
    ["python", "blender_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

try:
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }

    print(f"Sending: {json.dumps(init_request)}")
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()

    # Read response
    response = process.stdout.readline()
    print(f"Response: {response}")

    # Send tools/list request
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }

    print(f"\nSending: {json.dumps(tools_request)}")
    process.stdin.write(json.dumps(tools_request) + "\n")
    process.stdin.flush()

    response = process.stdout.readline()
    print(f"Response: {response[:200]}...")

    # Send create_object request
    create_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "create_object",
            "arguments": {
                "type": "cube",
                "name": "TestCube",
                "location": [0, 0, 0],
                "size": 2.0
            }
        }
    }

    print(f"\nSending create_object: {json.dumps(create_request)}")
    process.stdin.write(json.dumps(create_request) + "\n")
    process.stdin.flush()

    # Read response
    print("\nWaiting for create_object response...")
    response = process.stdout.readline()
    print(f"Response: {response}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    process.terminate()
    process.wait()
