#!/usr/bin/env python3
"""
Integrates Modular Expert Fabric Engine endpoints into giant_gpt_kernel.py
"""

import os
from expert_fabric_engine import ExpertFabricEngine, ExpertManifest

def add_expert_endpoints():
    kernel_file = "/Users/alep/.gemini/antigravity-ide/scratch/hdar-canonical/giant_gpt_kernel.py"
    with open(kernel_file, "r") as f:
        content = f.read()

    if "/expert/run" in content:
        print("Expert endpoints already integrated into giant_gpt_kernel.py.")
        return

    # Append expert handler endpoints to MockKernelHandler
    injection_point = "elif parsed_path == '/tool/register':"
    
    expert_code = '''elif parsed_path == '/expert/list':
            fabric = ExpertFabricEngine()
            self._send_json(200, {"experts": fabric.list_experts()})

        elif parsed_path == '/expert/run':
            prompt = data.get('prompt', '')
            fabric = ExpertFabricEngine()
            result = fabric.execute_fabric(prompt, context=data.get('context', {}))
            self._send_json(200, result)

        ''' + injection_point

    updated_content = content.replace(injection_point, expert_code)
    
    # Also add import at top of giant_gpt_kernel.py
    updated_content = "from expert_fabric_engine import ExpertFabricEngine\n" + updated_content

    with open(kernel_file, "w") as f:
        f.write(updated_content)

    print("✅ Successfully integrated /expert/list and /expert/run into giant_gpt_kernel.py!")

if __name__ == "__main__":
    add_expert_endpoints()
