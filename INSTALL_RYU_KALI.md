# Installing Ryu on Kali Linux (Python 3.13 Fix)

## Problem

Ryu has compatibility issues with Python 3.13 and newer setuptools versions. The error occurs because Ryu's setup.py uses deprecated setuptools APIs.

## Solution 1: Install Ryu from Source (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Install older setuptools first
pip install "setuptools<70.0"

# Clone Ryu repository
cd /tmp
git clone https://github.com/faucetsdn/ryu.git
cd ryu

# Install Ryu
pip install .

# Go back to project
cd /home/kali/Desktop/hhh/fog-computing-project
```

## Solution 2: Use Python 3.11 or 3.12 (Alternative)

If you have Python 3.11 or 3.12 available:

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Or Python 3.12
python3.12 -m venv venv

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Solution 3: Install Ryu Dependencies Manually

```bash
source venv/bin/activate

# Install dependencies first
pip install "setuptools<70.0"
pip install eventlet lxml netaddr oslo.config oslo.i18n oslo.serialization tinyrpc ovs

# Install Ryu with specific setuptools version
pip install --no-build-isolation ryu
```

## Solution 4: Patch Ryu Installation

```bash
source venv/bin/activate

# Install older setuptools
pip install "setuptools<70.0" "wheel<0.43.0"

# Try installing Ryu
pip install ryu --no-build-isolation
```

## Solution 5: Use System Python (If Available)

If your system has Python 3.11 or 3.12:

```bash
# Check available Python versions
ls /usr/bin/python3*

# Use Python 3.11 or 3.12
/usr/bin/python3.11 -m venv venv
# or
/usr/bin/python3.12 -m venv venv

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Quick Fix Script

Create and run this script:

```bash
cat > install_ryu_fix.sh << 'EOF'
#!/bin/bash
source venv/bin/activate

echo "Installing compatible setuptools..."
pip install "setuptools<70.0" "wheel<0.43.0"

echo "Installing Ryu dependencies..."
pip install eventlet lxml netaddr oslo.config oslo.i18n oslo.serialization tinyrpc ovs

echo "Installing Ryu from source..."
cd /tmp
git clone https://github.com/faucetsdn/ryu.git
cd ryu
pip install .
cd -

echo "Ryu installation complete!"
ryu-manager --version
EOF

chmod +x install_ryu_fix.sh
./install_ryu_fix.sh
```

## Verify Installation

After installing, verify:

```bash
source venv/bin/activate
ryu-manager --version
python3 -c "import ryu; print('Ryu installed successfully')"
```

## Continue with Project Setup

Once Ryu is installed:

```bash
# Install remaining dependencies (skip Ryu)
pip install -r requirements.txt --ignore-installed ryu

# Or install all except Ryu
pip install numpy pandas scipy torch tensorflow stable-baselines3 paho-mqtt grpcio prometheus-client loguru
```

## Alternative: Use Docker for Ryu

If installation continues to fail, you can run Ryu in a Docker container:

```bash
# Pull Ryu Docker image
docker pull osrg/ryu

# Run Ryu controller
docker run -it --rm -v $(pwd)/sdn_controller:/ryu/app osrg/ryu ryu-manager /ryu/app/ryu_apps/ai_routing_app.py
```

## Check Your Python Version

```bash
python3 --version
```

If it's Python 3.13, consider using Solution 2 (Python 3.11/3.12) for better compatibility.

