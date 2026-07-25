#!/usr/bin/env python3
"""
HuggingFace Space Updater for josephrw/Endpoint

Upgrades the `/` route in app.py from a minimal text page to the full
unified MorphOS Dashboard with embedded CSC Engine interface, interactive terminal,
and OpenAPI spec tabs.
"""

import urllib.request
import json
import base64

import os
TOKEN = os.environ.get('HF_TOKEN', '')
SPACE_ID = 'josephrw/Endpoint'

# Fetch existing app.py from HF Space
url = f'https://huggingface.co/spaces/{SPACE_ID}/raw/main/app.py'
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
with urllib.request.urlopen(req) as resp:
    current_app_py = resp.read().decode('utf-8')

# Build the rich MorphOS dashboard HTML for home()
morphos_home_html = '''"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MorphOS Unified Dashboard — Self-Relaunching GPT Kernel</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-main: #0b0d14;
      --bg-card: rgba(22, 27, 38, 0.8);
      --border-color: rgba(255, 255, 255, 0.12);
      --accent-cyan: #00f2fe;
      --accent-blue: #4facfe;
      --text-main: #f0f4f8;
      --text-muted: #94a3b8;
      --font-sans: 'Inter', sans-serif;
      --font-mono: 'Fira Code', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg-main); color: var(--text-main); font-family: var(--font-sans); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    
    header { background: rgba(15, 18, 28, 0.95); border-bottom: 1px solid var(--border-color); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-size: 18px; font-weight: 800; display: flex; align-items: center; gap: 10px; }
    .badge { font-family: var(--font-mono); font-size: 11px; background: rgba(0, 242, 254, 0.15); color: var(--accent-cyan); border: 1px solid rgba(0, 242, 254, 0.3); padding: 2px 8px; border-radius: 12px; }
    
    .nav-tabs { display: flex; gap: 8px; }
    .tab-btn { background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
    .tab-btn.active, .tab-btn:hover { background: rgba(0, 242, 254, 0.15); color: var(--accent-cyan); border-color: rgba(0, 242, 254, 0.4); }

    main { flex: 1; position: relative; width: 100%; height: calc(100vh - 65px); }
    .tab-content { display: none; width: 100%; height: 100%; }
    .tab-content.active { display: block; }

    iframe { width: 100%; height: 100%; border: none; }
    
    .terminal-container { padding: 24px; height: 100%; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; max-width: 1000px; margin: 0 auto; }
    .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }
    h2 { font-size: 18px; font-weight: 700; margin-bottom: 12px; color: var(--accent-cyan); }
    input, textarea { width: 100%; background: #0d1117; border: 1px solid var(--border-color); border-radius: 8px; padding: 10px; color: #fff; font-family: var(--font-mono); font-size: 13px; margin-bottom: 10px; }
    button.action-btn { background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)); color: #000; font-weight: 700; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
    pre { background: #0d1117; padding: 12px; border-radius: 8px; font-family: var(--font-mono); font-size: 12px; color: #a5d6ff; overflow-x: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <header>
    <div class="logo">
      🌀 MorphOS Unified Dashboard
      <span class="badge">v4.0.0 Live</span>
    </div>
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('csc-tab', this)">CSC Interface</button>
      <button class="tab-btn" onclick="switchTab('kernel-tab', this)">GPT Kernel Execution</button>
      <button class="tab-btn" onclick="switchTab('api-tab', this)">OpenAPI Docs</button>
    </div>
  </header>
  
  <main>
    <!-- Tab 1: Embedded CSC Engine -->
    <div id="csc-tab" class="tab-content active">
      <iframe src="https://josephrw-csc-engine.hf.space"></iframe>
    </div>
    
    <!-- Tab 2: GPT Kernel Execution -->
    <div id="kernel-tab" class="tab-content">
      <div class="terminal-container">
        <div class="card">
          <h2>Terminal Command Execution (/terminal/run)</h2>
          <input type="text" id="cmd-input" value="echo 'Hello MorphOS Kernel!'" placeholder="Enter shell command..." />
          <button class="action-btn" onclick="runTerminal()">Execute Command</button>
          <pre id="cmd-out" style="margin-top:12px;">Result will appear here...</pre>
        </div>
        
        <div class="card">
          <h2>Python Execution (/python/run)</h2>
          <textarea id="py-input" rows="4">import math; print(f'Pi = {math.pi}')</textarea>
          <button class="action-btn" onclick="runPython()">Run Python Code</button>
          <pre id="py-out" style="margin-top:12px;">Result will appear here...</pre>
        </div>
      </div>
    </div>
    
    <!-- Tab 3: API Specs -->
    <div id="api-tab" class="tab-content">
      <iframe src="/docs"></iframe>
    </div>
  </main>

  <script>
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(tabId).classList.add('active');
      btn.classList.add('active');
    }
    
    async function runTerminal() {
      const cmd = document.getElementById('cmd-input').value;
      const out = document.getElementById('cmd-out');
      out.textContent = "Executing...";
      try {
        const res = await fetch('/terminal/run', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({command: cmd})
        });
        const data = await res.json();
        out.textContent = JSON.dumps(data, null, 2);
      } catch (e) {
        out.textContent = "Error: " + e;
      }
    }

    async function runPython() {
      const code = document.getElementById('py-input').value;
      const out = document.getElementById('py-out');
      out.textContent = "Executing...";
      try {
        const res = await fetch('/python/run', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({code: code})
        });
        const data = await res.json();
        out.textContent = JSON.dumps(data, null, 2);
      } catch (e) {
        out.textContent = "Error: " + e;
      }
    }
  </script>
</body>
</html>
"""'''

# Replace minimal home() return in app.py
old_home_start = current_app_py.find('@app.get("/", response_class=HTMLResponse, include_in_schema=False)')
old_home_end = current_app_py.find('@app.get("/favicon.ico"', old_home_start)

new_home_func = f'''@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return {morphos_home_html}


'''

updated_app_py = current_app_py[:old_home_start] + new_home_func + current_app_py[old_home_end:]

print(f"Original app.py length: {len(current_app_py)} | Updated app.py length: {len(updated_app_py)}")

# Commit updated app.py to Hugging Face via API
commit_payload = {
    "summary": "Upgrade / route to serve full MorphOS Unified Dashboard",
    "operations": [
        {
            "operation": "addOrUpdate",
            "path": "app.py",
            "content": base64.b64encode(updated_app_py.encode('utf-8')).decode('utf-8'),
            "encoding": "base64"
        }
    ]
}

commit_url = f"https://huggingface.co/api/spaces/{SPACE_ID}/commit/main"
req_commit = urllib.request.Request(
    commit_url,
    data=json.dumps(commit_payload).encode('utf-8'),
    headers={
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req_commit) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    print("✅ Successfully committed MorphOS Dashboard to josephrw/Endpoint!")
    print("Commit info:", res)
except Exception as e:
    print("❌ Commit error:", e)
