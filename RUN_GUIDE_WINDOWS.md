# How to Run on Windows

## Important Note

This project is designed for **Linux** and requires:
- Root access for network emulation (Mininet)
- Linux networking tools (Open vSwitch, etc.)

**Windows users have two options:**

## Option 1: Use WSL2 (Recommended)

### Setup WSL2

1. **Install WSL2**:
   ```powershell
   wsl --install
   ```

2. **Install Ubuntu 20.04 or later**:
   ```powershell
   wsl --install -d Ubuntu-20.04
   ```

3. **Open Ubuntu terminal** and follow the Linux instructions in `RUN_GUIDE.md`

### Transfer Project to WSL2

```powershell
# In PowerShell, copy project to WSL
wsl cp -r "C:\Users\Lenovo\Desktop\eniad IRSI\projet fog final" ~/fog-project
```

Then in WSL:
```bash
cd ~/fog-project
# Follow Linux instructions
```

## Option 2: Use Linux VM

1. Install VirtualBox or VMware
2. Create Ubuntu 20.04 VM
3. Transfer project files to VM
4. Follow Linux instructions

## Option 3: Run Components Separately (Limited)

Some components can run on Windows without network emulation:

### Run AI Models Only (Testing)

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Test LSTM model
python ai_models/lstm/model.py

# Test Autoencoder
python ai_models/autoencoder/model.py

# Test RL agent
python ai_models/rl/dqn_agent.py
```

### Run MQTT Client (Windows Compatible)

```powershell
# Install Mosquitto for Windows or use Docker
docker run -it -p 1883:1883 eclipse-mosquitto

# Run IoT client
python iot/mqtt_client.py
```

## Recommended: Use WSL2

For full functionality, **WSL2 is strongly recommended** as it provides:
- Native Linux environment
- Root access for network emulation
- All required tools and dependencies

Follow the Linux guide (`RUN_GUIDE.md`) in WSL2.

