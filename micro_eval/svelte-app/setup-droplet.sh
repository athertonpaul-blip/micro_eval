#!/bin/bash
# Initial setup script for a fresh Ubuntu 22.04 Digital Ocean droplet
# Run as root or with sudo

set -e

echo "=== Micro Evals Droplet Setup ==="

# Update system
echo "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Node.js 20
echo "Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Verify Node.js installation
node --version
npm --version

# Install PostgreSQL
echo "Installing PostgreSQL..."
apt-get install -y postgresql postgresql-contrib

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
echo "Setting up database..."
DB_PASSWORD=$(openssl rand -base64 32)
sudo -u postgres psql -c "CREATE USER microevals WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE microevals OWNER microevals;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE microevals TO microevals;"

echo "Database password: $DB_PASSWORD"
echo "Save this password! You'll need it for the .env file."

# Install Caddy for HTTPS
echo "Installing Caddy..."
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

# Install PM2 globally
echo "Installing PM2..."
npm install -g pm2

# Create app directory
echo "Creating app directory..."
mkdir -p /opt/microevals
cd /opt/microevals

# Clone repository (replace with your repo URL)
echo "Clone your repository to /opt/microevals"
echo "Example: git clone https://github.com/YOUR_USERNAME/micro-evals.git ."

# Create environment file template
echo "Creating environment file template..."
cat > /opt/microevals/svelte-app/.env << EOF
DATABASE_URL=postgresql://microevals:$DB_PASSWORD@localhost:5432/microevals
NODE_ENV=production
PORT=3000
EOF

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Clone your repository: cd /opt/microevals && git clone YOUR_REPO ."
echo "2. Configure Caddy: Edit /etc/caddy/Caddyfile"
echo "3. Install app dependencies: cd svelte-app && npm install"
echo "4. Run migrations: npm run db:push"
echo "5. Seed database: npm run db:seed"
echo "6. Build app: npm run build"
echo "7. Start with PM2: pm2 start ecosystem.config.cjs --env production"
echo "8. Save PM2 process list: pm2 save"
echo "9. Setup PM2 startup: pm2 startup"
echo ""
echo "Caddyfile example:"
echo "yourdomain.com {"
echo "    reverse_proxy localhost:3000"
echo "}"
