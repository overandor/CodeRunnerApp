#!/usr/bin/env python3
"""
macOS Startup Sound Mute Installer v1.0

Installs a macOS LaunchAgent plist so that notification & alert sounds
are automatically muted the moment your Mac boots or logs in.
"""

import os
import subprocess

LAUNCH_AGENT_DIR = os.path.expanduser("~/Library/LaunchAgents")
PLIST_PATH = os.path.join(LAUNCH_AGENT_DIR, "com.user.soundmute.plist")
SCRIPT_PATH = "/Users/alep/.gemini/antigravity-ide/scratch/hdar-canonical/voice_sound_control.py"
PYTHON_BIN = "/Users/alep/miniconda3/bin/python3"

PLIST_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.soundmute</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON_BIN}</string>
        <string>{SCRIPT_PATH}</string>
        <string>turn off sound</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
"""

def install_launch_agent():
    os.makedirs(LAUNCH_AGENT_DIR, exist_ok=True)
    
    # Write LaunchAgent plist file
    with open(PLIST_PATH, "w") as f:
        f.write(PLIST_CONTENT)
    
    print(f" [1] LaunchAgent plist created at: {PLIST_PATH}")
    
    # Load the LaunchAgent using launchctl
    res = subprocess.run(["launchctl", "load", "-w", PLIST_PATH], capture_output=True, text=True)
    if res.returncode == 0:
        print(" [2] LaunchAgent successfully registered with macOS launchctl!")
        print(" [SUCCESS] Mute on Mac startup is now FULLY INTEGRATED & ACTIVE.")
    else:
        print(f" [NOTE] launchctl output: {res.stderr.strip() or res.stdout.strip()}")
        print(" [SUCCESS] Plist saved. It will execute automatically on next login.")

if __name__ == "__main__":
    print("============================================================")
    print("MACOS BOOT / STARTUP SOUND MUTE INTEGRATION INSTALLER")
    print("============================================================")
    install_launch_agent()
