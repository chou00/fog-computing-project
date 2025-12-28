#!/bin/bash
# Fix Ryu installation on Kali Linux with Python 3.13

set -e

echo "=== Fixing Ryu Installation ==="

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "ERROR: Virtual environment not found. Run: python3 -m venv venv"
        exit 1
    fi
fi

echo "Installing compatible setuptools..."
pip install "setuptools<70.0" "wheel<0.43.0"

echo "Installing Ryu dependencies..."
pip install eventlet lxml netaddr oslo.config oslo.i18n oslo.serialization tinyrpc ovs

echo "Installing Ryu from source with patch..."
cd /tmp

# Remove old Ryu if exists
rm -rf ryu

# Clone Ryu
git clone https://github.com/faucetsdn/ryu.git
cd ryu

# Patch Ryu's hooks.py to fix Python 3.13 compatibility
echo "Patching Ryu for Python 3.13 compatibility..."
cat > /tmp/patch_ryu.py << 'PATCH_EOF'
import os
import re

hooks_file = "ryu/hooks.py"
if os.path.exists(hooks_file):
    with open(hooks_file, 'r') as f:
        content = f.read()
    
    # Replace the problematic line
    old_line = "_main_module()._orig_get_script_args = easy_install.get_script_args"
    new_line = "# _main_module()._orig_get_script_args = easy_install.get_script_args  # Commented out for Python 3.13 compatibility"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        with open(hooks_file, 'w') as f:
            f.write(content)
        print("✓ Patched ryu/hooks.py")
    else:
        print("⚠ Could not find line to patch in ryu/hooks.py")
else:
    print("⚠ ryu/hooks.py not found")
PATCH_EOF

python3 /tmp/patch_ryu.py

# Install Ryu
echo "Installing Ryu..."
pip install . --no-build-isolation

# Go back to project directory
cd - > /dev/null

echo ""
echo "=== Verifying Installation ==="
python3 -c "import ryu; print('✓ Ryu Python module imported successfully')" || {
    echo "✗ Ryu import failed"
    exit 1
}

# Try to get version
ryu-manager --version 2>/dev/null || echo "⚠ ryu-manager command not found, but Python module works"

echo ""
echo "=== Ryu Installation Complete! ==="
echo "You can now continue with: pip install -r requirements.txt --ignore-installed ryu"
