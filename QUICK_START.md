# Quick Start Guide

## For Linux Users

### 1. Initial Setup (One-time)

```bash
# Navigate to project directory
cd "path/to/projet fog final"

# Run setup script
bash scripts/setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Start Everything (Quick Start)

Open **4 separate terminals**:

**Terminal 1 - Services:**
```bash
docker-compose up -d
```

**Terminal 2 - SDN Controller:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

**Terminal 3 - Network:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo python3 fogbed/topology.py
```

**Terminal 4 - Traffic:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
python3 iot/traffic_generator.py --pattern periodic --devices 10 --duration 60
```

### 3. Or Use the Quick Start Script

```bash
sudo bash scripts/quick_start.sh distributed_ai
```

## For Windows Users

### Option 1: Use WSL2 (Recommended)

1. Install WSL2: `wsl --install`
2. Open Ubuntu terminal
3. Follow Linux instructions above

### Option 2: Test AI Models Only

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Test AI models (no network required)
python run.py test-ai
```

## Verify Installation

```bash
# Test AI models
python3 run.py test-ai

# Check dependencies
pip list | grep -E "torch|ryu|paho|grpc"
```

## Common Commands

```bash
# Run controller
python3 run.py controller --architecture distributed_ai

# Run traffic generator
python3 run.py traffic --pattern periodic --devices 20

# Run tests
python3 run.py test --architecture distributed_ai --scenario baseline

# Stop everything
sudo bash scripts/stop.sh
```

## Troubleshooting

**"Permission denied"**: Use `sudo` for network commands

**"Module not found"**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**"Port in use"**: 
```bash
sudo lsof -i :6633  # Find process
sudo kill -9 <PID>   # Kill it
```

## Next Steps

1. Read `RUN_GUIDE.md` for detailed instructions
2. Check `technical_sheet.tex` for architecture details
3. View results in `results/metrics/`

