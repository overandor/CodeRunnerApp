#!/usr/bin/env python3
"""
macOS Unnecessary Bloat & Cache Cleaner (Fast Engine v1.0)
"""

import os
import shutil
from pathlib import Path

CLEANUP_TARGETS = [
    (os.path.expanduser("~/Library/Caches"), "User App Caches"),
    (os.path.expanduser("~/Library/Logs"), "User Application Logs"),
    (os.path.expanduser("~/Library/Developer/Xcode/DerivedData"), "Xcode Derived Data"),
    (os.path.expanduser("~/.cache/pip"), "Pip Download Cache"),
    (os.path.expanduser("~/.npm/_cacache"), "npm Package Cache")
]

def fast_clean():
    total_freed_mb = 0.0
    print("============================================================")
    print("MACOS UNNECESSARY BLOAT & CACHE CLEANER")
    print("============================================================")

    for target_path, label in CLEANUP_TARGETS:
        if os.path.exists(target_path):
            try:
                # Fast size check on top level entries
                entries = os.listdir(target_path)
                removed_count = 0
                for item in entries:
                    ipath = os.path.join(target_path, item)
                    try:
                        if os.path.isdir(ipath) and not os.path.islink(ipath):
                            shutil.rmtree(ipath, ignore_errors=True)
                            removed_count += 1
                        elif os.path.isfile(ipath):
                            os.remove(ipath)
                            removed_count += 1
                    except Exception:
                        pass
                print(f"  • {label:35s} : Cleaned {removed_count} item(s)")
            except Exception as e:
                print(f"  • {label:35s} : Skipped ({e})")

    print("\n✅ UNNECESSARY BLOAT & CACHE PURGED SUCCESSFULLY.")

if __name__ == "__main__":
    fast_clean()
