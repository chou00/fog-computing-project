#!/bin/bash
# Alternative Ryu installation method - install without build isolation

set -e

echo "=== Alternative Ryu Installation Method ==="

if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "ERROR: Virtual environment not found"
        exit 1
    fi
fi

echo "Installing setuptools and dependencies..."
pip install "setuptools<70.0" "wheel<0.43.0"
pip install eventlet lxml netaddr oslo.config oslo.i18n oslo.serialization tinyrpc ovs

echo "Cloning and patching Ryu..."
cd /tmp
rm -rf ryu
git clone https://github.com/faucetsdn/ryu.git
cd ryu

# Create a simple patch file
cat > /tmp/ryu_patch.diff << 'DIFF_EOF'
--- a/ryu/hooks.py
+++ b/ryu/hooks.py
@@ -33,7 +33,10 @@ def save_orig():
     import setuptools.command.easy_install as easy_install
     import setuptools.command.install as install
 
-    _main_module()._orig_get_script_args = easy_install.get_script_args
+    # Commented out for Python 3.13 compatibility
+    # _main_module()._orig_get_script_args = easy_install.get_script_args
+    if hasattr(easy_install, 'get_script_args'):
+        _main_module()._orig_get_script_args = easy_install.get_script_args
 DIFF_EOF

# Apply patch using Python
python3 << 'PYTHON_EOF'
import os
import sys

hooks_file = "ryu/hooks.py"
if os.path.exists(hooks_file):
    with open(hooks_file, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    patched = False
    for line in lines:
        if '_orig_get_script_args = easy_install.get_script_args' in line and not patched:
            # Replace with safe version
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + '# Fixed for Python 3.13 compatibility\n')
            new_lines.append(' ' * indent + 'try:\n')
            new_lines.append(' ' * indent + '    _main_module()._orig_get_script_args = easy_install.get_script_args\n')
            new_lines.append(' ' * indent + 'except AttributeError:\n')
            new_lines.append(' ' * indent + '    pass  # Attribute not available in newer setuptools\n')
            patched = True
        else:
            new_lines.append(line)
    
    if patched:
        with open(hooks_file, 'w') as f:
            f.writelines(new_lines)
        print("✓ Successfully patched ryu/hooks.py")
    else:
        print("⚠ Could not find line to patch")
else:
    print("✗ ryu/hooks.py not found")
    sys.exit(1)
PYTHON_EOF

# Install with no build isolation
echo "Installing Ryu..."
pip install . --no-build-isolation || {
    echo "Trying alternative installation method..."
    python3 setup.py install
}

cd - > /dev/null

echo ""
echo "=== Verifying ==="
python3 -c "import ryu; print('✓ Ryu installed successfully!')"

