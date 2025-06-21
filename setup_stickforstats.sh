#!/bin/bash

# StickForStats Automated Deployment Script for Hetzner
# This script sets up everything needed to run StickForStats on Ubuntu 22.04

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Header
echo "================================================"
echo "   StickForStats Automated Setup for Hetzner"
echo "================================================"
echo ""

# Get server IP
SERVER_IP=$(curl -s https://ipinfo.io/ip)
print_status "Server IP detected: $SERVER_IP"

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    ufw \
    nginx \
    certbot \
    python3-certbot-nginx \
    supervisor \
    redis-server \
    htop \
    tmux

# Install Python 3.10
print_status "Installing Python 3.10..."
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.10 python3.10-venv python3.10-dev python3-pip

# Install Node.js 18
print_status "Installing Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install PostgreSQL 15
print_status "Installing PostgreSQL 15..."
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt update
apt install -y postgresql-15 postgresql-client-15

# Create stickforstats user
print_status "Creating stickforstats user..."
if ! id -u stickforstats >/dev/null 2>&1; then
    useradd -m -s /bin/bash stickforstats
    usermod -aG sudo stickforstats
fi

# Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE stickforstats_db;
CREATE USER stickforstats_user WITH PASSWORD 'StickForStats2024!';
GRANT ALL PRIVILEGES ON DATABASE stickforstats_db TO stickforstats_user;
EOF

# Create application directory
print_status "Creating application directory..."
mkdir -p /home/stickforstats/app
mkdir -p /home/stickforstats/logs
mkdir -p /home/stickforstats/static
mkdir -p /home/stickforstats/media
chown -R stickforstats:stickforstats /home/stickforstats

# Clone repository
print_status "Cloning repository..."
REPO_URL="https://github.com/visvikbharti/stickforstats.git"
sudo -u stickforstats git clone $REPO_URL /home/stickforstats/app

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
cd /home/stickforstats/app
sudo -u stickforstats python3.10 -m venv venv
sudo -u stickforstats ./venv/bin/pip install --upgrade pip

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    sudo -u stickforstats ./venv/bin/pip install -r requirements.txt
    sudo -u stickforstats ./venv/bin/pip install gunicorn
fi

# Setup environment variables
print_status "Creating environment configuration..."
cat > /home/stickforstats/app/.env <<EOF
# Django settings
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://stickforstats_user:StickForStats2024!@localhost/stickforstats_db

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Static files
STATIC_ROOT=/home/stickforstats/static/
MEDIA_ROOT=/home/stickforstats/media/
EOF
chown stickforstats:stickforstats /home/stickforstats/app/.env

# Setup Django
print_status "Setting up Django..."
cd /home/stickforstats/app
sudo -u stickforstats ./venv/bin/python manage.py collectstatic --noinput || true
sudo -u stickforstats ./venv/bin/python manage.py migrate

# Create superuser
print_status "Creating Django superuser..."
print_warning "Please create your admin account:"
sudo -u stickforstats ./venv/bin/python manage.py createsuperuser

# Setup frontend
if [ -d "frontend" ]; then
    print_status "Building React frontend..."
    cd /home/stickforstats/app/frontend
    sudo -u stickforstats npm install
    sudo -u stickforstats NODE_OPTIONS="--max-old-space-size=4096" npm run build || sudo -u stickforstats npm run build
    
    # Copy built files to static directory
    if [ -d "build" ]; then
        cp -r build/* /home/stickforstats/static/
    fi
fi

# Configure Gunicorn with Supervisor
print_status "Configuring Gunicorn service..."
cat > /etc/supervisor/conf.d/stickforstats.conf <<EOF
[program:stickforstats]
command=/home/stickforstats/app/venv/bin/gunicorn stickforstats.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/home/stickforstats/app
user=stickforstats
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/stickforstats/logs/gunicorn.log
environment=PATH="/home/stickforstats/app/venv/bin"
EOF

# Configure NGINX
print_status "Configuring NGINX..."
cat > /etc/nginx/sites-available/stickforstats <<EOF
server {
    listen 80;
    server_name $SERVER_IP;
    
    client_max_body_size 100M;
    
    location / {
        root /home/stickforstats/static;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias /home/stickforstats/static/;
    }
    
    location /media/ {
        alias /home/stickforstats/media/;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/stickforstats /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configure firewall
print_status "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Start services
print_status "Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start stickforstats
systemctl restart nginx
systemctl enable postgresql
systemctl enable redis-server
systemctl enable supervisor

# Final setup
print_status "Running final configurations..."
cd /home/stickforstats/app
chown -R stickforstats:stickforstats /home/stickforstats

# Success message
echo ""
echo "================================================"
echo -e "${GREEN}   StickForStats Setup Complete!${NC}"
echo "================================================"
echo ""
echo "Your application is now available at:"
echo -e "  ${GREEN}http://$SERVER_IP${NC}"
echo ""
echo "Admin panel:"
echo -e "  ${GREEN}http://$SERVER_IP/admin${NC}"
echo ""
echo "Useful commands:"
echo "  supervisorctl status         - Check app status"
echo "  supervisorctl restart all    - Restart app"
echo "  tail -f /home/stickforstats/logs/gunicorn.log - View logs"
echo ""
echo "Next steps:"
echo "1. Test your application at http://$SERVER_IP"
echo "2. Configure a domain name (optional)"
echo "3. Setup SSL with: certbot --nginx"
echo ""
print_warning "Remember to save your database password: StickForStats2024!"
echo ""