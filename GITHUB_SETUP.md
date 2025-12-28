# How to Push to GitHub

Step-by-step guide to push this project to GitHub.

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the **"+"** icon → **"New repository"**
3. Fill in:
   - **Repository name**: `fog-computing-project` (or your preferred name)
   - **Description**: "AI-Driven Distributed Fog Load Balancing & Anomaly-Aware Routing"
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 2: Initialize Git Repository (if not already done)

```bash
# Navigate to project directory
cd "C:\Users\Lenovo\Desktop\eniad IRSI\projet fog final"

# Initialize git repository
git init

# Check status
git status
```

## Step 3: Add Files to Git

```bash
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status
```

## Step 4: Create Initial Commit

```bash
# Create first commit
git commit -m "Initial commit: AI-Driven Distributed Fog Load Balancing & Anomaly-Aware Routing

- Complete fog computing architecture implementation
- Three architecture variants (centralized, distributed no-AI, distributed AI)
- AI components: LSTM, Autoencoder, RL agent
- SDN controller with OpenFlow
- MQTT and gRPC communication
- Prometheus and Grafana monitoring
- Comprehensive test scenarios"
```

## Step 5: Add GitHub Remote

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/fog-computing-project.git

# Verify remote
git remote -v
```

## Step 6: Push to GitHub

```bash
# Push to GitHub (first time)
git branch -M main
git push -u origin main
```

If you get authentication errors, you may need to:

### Option A: Use Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use token as password when pushing

### Option B: Use SSH (Recommended)
```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to GitHub
# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key

# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/fog-computing-project.git

# Push again
git push -u origin main
```

## Step 7: Verify Upload

1. Go to your GitHub repository page
2. Verify all files are uploaded
3. Check that README.md displays correctly

## Complete Commands (Copy-Paste Ready)

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Navigate to project
cd "C:\Users\Lenovo\Desktop\eniad IRSI\projet fog final"

# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: AI-Driven Distributed Fog Load Balancing & Anomaly-Aware Routing"

# Add remote (HTTPS)
git remote add origin https://github.com/YOUR_USERNAME/fog-computing-project.git

# Push
git branch -M main
git push -u origin main
```

## Updating Repository

After making changes:

```bash
# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push
git push
```

## Adding More Files Later

```bash
# Add specific file
git add path/to/file.py

# Or add all changes
git add .

# Commit
git commit -m "Add new feature"

# Push
git push
```

## Creating Releases

For important milestones:

```bash
# Create a tag
git tag -a v1.0.0 -m "First release: Complete implementation"

# Push tags
git push origin v1.0.0
```

Then on GitHub: Releases → Draft a new release → Select tag → Publish

## Troubleshooting

### "Repository not found"
- Check repository name and username are correct
- Verify you have access to the repository

### "Authentication failed"
- Use Personal Access Token instead of password
- Or set up SSH keys

### "Large files error"
- Check .gitignore is working
- Remove large files: `git rm --cached large_file.bin`

### "Merge conflicts"
```bash
# Pull latest changes first
git pull origin main

# Resolve conflicts, then:
git add .
git commit -m "Resolve conflicts"
git push
```

## Best Practices

1. **Commit often** with descriptive messages
2. **Don't commit**:
   - `venv/` (virtual environment)
   - `results/` (test outputs)
   - `*.log` files
   - Large model files
3. **Use .gitignore** (already configured)
4. **Write clear commit messages**

## Repository Settings on GitHub

After pushing, configure:

1. **Description**: Add project description
2. **Topics**: Add tags like `fog-computing`, `sdn`, `ai`, `networking`
3. **Website**: Add project URL if you have one
4. **README**: Should display automatically

## Example Repository Topics

- `fog-computing`
- `sdn`
- `openflow`
- `ai`
- `machine-learning`
- `lstm`
- `reinforcement-learning`
- `mqtt`
- `grpc`
- `prometheus`
- `grafana`
- `networking`
- `distributed-systems`

## Next Steps

1. ✅ Push to GitHub
2. Add repository description and topics
3. Create a release for v1.0.0
4. Share the repository link
5. Continue development and push updates regularly

