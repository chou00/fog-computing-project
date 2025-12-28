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

echo "Installing Ryu from source..."
cd /tmp

# Remove old Ryu if exists
rm -rf ryu

# Clone Ryu
git clone https://github.com/faucetsdn/ryu.git
cd ryu

# Install Ryu
pip install .

# Go back to project directory
cd - > /dev/null

echo ""
echo "=== Verifying Installation ==="
ryu-manager --version || echo "Warning: ryu-manager not in PATH, but installation may have succeeded"

python3 -c "import ryu; print('✓ Ryu Python module imported successfully')" || {
    echo "✗ Ryu import failed"
    exit 1
}

echo ""
echo "=== Ryu Installation Complete! ==="
echo "You can now continue with: pip install -r requirements.txt"

