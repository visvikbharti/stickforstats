# 🚀 Hetzner Step-by-Step Deployment

## Step 1: Create Project
1. Click the **"New project"** button (red button in the center)
2. Name it: `StickForStats`
3. Click Create

## Step 2: Generate SSH Key (on your Mac)
Open Terminal and run:
```bash
# Check if you have an SSH key
ls ~/.ssh/id_rsa.pub

# If not, create one:
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Press Enter for all prompts (use default location, no passphrase for simplicity)

# Copy your public key
cat ~/.ssh/id_rsa.pub
```
**IMPORTANT**: Copy the entire output (starts with `ssh-rsa`)

## Step 3: Add SSH Key to Hetzner
1. In your new project, go to **Security** → **SSH Keys**
2. Click **"Add SSH Key"**
3. Paste your public key
4. Name it: `MacBook SSH Key`
5. Click Add

## Step 4: Create Server
1. Go to **Servers** in the left menu
2. Click **"Create Server"**
3. Configure:
   - **Location**: Ashburn (or closest to you)
   - **Image**: Ubuntu 22.04
   - **Type**: Click "Dedicated vCPU" tab, then select **CX31** (2 vCPU, 8GB RAM)
   - **Network**: Leave default (Public IPv4 + IPv6)
   - **SSH Keys**: Select your "MacBook SSH Key"
   - **Name**: `stickforstats-server`
4. Click **"Create & Buy now"**

## Step 5: Note Your Server IP
After creation, you'll see your server with an IP address like `65.21.XXX.XXX`
**Save this IP address!**

## Step 6: Upload Setup Script
On your Mac, run:
```bash
# Replace YOUR_SERVER_IP with the actual IP
scp /Users/vishalbharti/Downloads/StickForStats_Migration/new_project/setup_stickforstats.sh root@YOUR_SERVER_IP:~/
```

## Step 7: Connect & Deploy
```bash
# Connect to server
ssh root@YOUR_SERVER_IP

# Make script executable
chmod +x setup_stickforstats.sh

# Run the setup (this takes ~20 minutes)
./setup_stickforstats.sh
```

## Step 8: Follow Script Prompts
The script will ask for:
1. **GitHub Repository URL**: Enter `https://github.com/visvikbharti/stickforstats.git`
2. **Create Django superuser**: Choose username/password for admin access

## 🎉 Done!
Your app will be available at:
- Main app: `http://YOUR_SERVER_IP`
- Admin panel: `http://YOUR_SERVER_IP/admin`

## 📝 Important Commands
```bash
# Check app status
supervisorctl status

# View logs
tail -f /home/stickforstats/logs/gunicorn.log

# Restart app
supervisorctl restart stickforstats
```

## 🔒 Optional: Setup Domain & SSL
If you have a domain:
1. Point domain to server IP
2. Run: `certbot --nginx -d yourdomain.com`