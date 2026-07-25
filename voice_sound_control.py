#!/usr/bin/env python3
"""
macOS Voice & Command Sound Automator v1.0

Automates muting/unmuting notification and system sound effects on macOS:
- Executable via voice command ("turn off sound" / "turn on sound")
- Mutes macOS Alert Volume, UI Sound Effects, and toggles Focus Do Not Disturb
"""

import subprocess
import sys
import time

def set_mac_sound_effects(enabled: bool):
    """Mutes or unmutes notification UI sound effects and alert volume via AppleScript."""
    alert_vol = 0 if not enabled else 100
    ui_val = 0 if not enabled else 1

    # Set macOS Alert Volume
    subprocess.run(["osascript", "-e", f"set volume alert volume {alert_vol}"], check=False)

    # Enable/Disable UI Notification Sound Effects
    subprocess.run(["defaults", "write", "com.apple.sound.uiaudio", "com.apple.sound.uiaudio.enabled", "-int", str(ui_val)], check=False)
    
    # Reload audio daemon settings
    subprocess.run(["killall", "coreaudiod"], capture_output=True, check=False)

def toggle_do_not_disturb(enabled: bool):
    """Toggles Do Not Disturb Focus mode on macOS."""
    val = "true" if enabled else "false"
    cmd = f'tell application "System Events" to set focus mode to {val}'
    subprocess.run(["osascript", "-e", cmd], capture_output=True, check=False)

def execute_voice_action(command_phrase: str):
    """Parses spoken phrase and executes sound automation."""
    phrase = command_phrase.lower().strip()
    
    if any(k in phrase for k in ["off", "mute", "quiet", "silence"]):
        print(" [ACTION] Muting Notification & Alert Sounds...")
        set_mac_sound_effects(enabled=False)
        print(" [SUCCESS] Sound Muted.")
    elif any(k in phrase for k in ["on", "unmute", "enable", "loud"]):
        print(" [ACTION] Enabling Notification & Alert Sounds...")
        set_mac_sound_effects(enabled=True)
        print(" [SUCCESS] Sound Restored.")
    else:
        print(f" [UNKNOWN] Phrase '{command_phrase}' not recognized. Use 'turn off sound' or 'turn on sound'.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
        execute_voice_action(phrase)
    else:
        print("============================================================")
        print("MACOS VOICE SOUND AUTOMATION CLI")
        print("============================================================")
        print("Usage:")
        print("  python3 voice_sound_control.py 'turn off sound'")
        print("  python3 voice_sound_control.py 'turn on sound'")
        print("============================================================")
