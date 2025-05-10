#!/usr/bin/env python3
import os
import re
from packaging import version

def get_current_version():
    with open("setup.py", "r") as f:
        content = f.read()
        version_match = re.search(r'version="([^"]+)"', content)
        if version_match:
            return version_match.group(1)
    return "0.0.0"  # Default if not found

def bump_version(current_version, bump_type):
    v = version.parse(current_version)
    
    # For non-standard version objects, convert to string and parse components
    if not hasattr(v, 'release'):
        parts = str(v).split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
    else:
        # For standard version objects
        major, minor, patch = v.release[0], v.release[1], v.release[2]
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def update_setup_py(new_version):
    with open("setup.py", "r") as f:
        content = f.read()
    
    updated_content = re.sub(
        r'version="[^"]+"',
        f'version="{new_version}"',
        content
    )
    
    with open("setup.py", "w") as f:
        f.write(updated_content)

if __name__ == "__main__":
    bump_type = os.environ.get("BUMP_TYPE", "patch")
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)
    
    print(f"Current version: {current_version}")
    print(f"Bump type: {bump_type}")
    print(f"New version: {new_version}")
    
    update_setup_py(new_version) 