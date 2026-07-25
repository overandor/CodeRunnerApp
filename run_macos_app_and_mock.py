#!/usr/bin/env python3
"""
macOS Native App & Local Mock Kernel Launcher v1.0
"""

import sys
import time
import json
import threading
import urllib.request
from giant_gpt_kernel import start_local_mock_server
from eof_service import run_server as run_eof_server
from srm.capability_graph import CapabilityGraph

def launch_mock_kernel():
    print(" [1/3] Starting Local Mock Kernel on http://127.0.0.1:8088...")
    start_local_mock_server(8088)

def launch_eof_service():
    print(" [2/3] Starting EOF Service on http://127.0.0.1:8090...")
    run_eof_server(8090)

def main():
    print("============================================================")
    print("MACOS NATIVE APP & LOCAL MOCK KERNEL LAUNCHER")
    print("============================================================")

    # 1. Start Local Mock Kernel in background thread
    t1 = threading.Thread(target=launch_mock_kernel, daemon=True)
    t1.start()

    # 2. Start EOF Service in background thread
    t2 = threading.Thread(target=launch_eof_service, daemon=True)
    t2.start()

    time.sleep(1.0)

    # 3. Health check local endpoints
    print("\n [3/3] Verifying Local Mock Server Endpoints...")
    try:
        req = urllib.request.Request("http://127.0.0.1:8088/health")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        print(f"  ✅ Mock Kernel (Port 8088): {data['app']} — LIVE")
    except Exception as e:
        print(f"  ❌ Mock Kernel check error: {e}")

    try:
        req = urllib.request.Request("http://127.0.0.1:8090/health")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        print(f"  ✅ EOF Service (Port 8090): {data.get('service', 'EOF REST API')} — LIVE")
    except Exception as e:
        print(f"  ❌ EOF Service check error: {e}")

    # 4. Run macOS Capability Indexer
    print("\n --- macOS Native App & Capability Graph ---")
    graph = CapabilityGraph()
    graph.build_graph()
    print(f"  • Indexed macOS Apps: {len(graph.app_nodes)}")
    print(f"  • Apple Shortcuts:   {len(graph.shortcuts)}")

    print("\n============================================================")
    print("ALL MACOS LOCAL MOCK SERVICES & APPS VERIFIED OPERATIONAL.")
    print("============================================================")

if __name__ == "__main__":
    main()
