#!/bin/bash
# Deployment script for Digital Ocean droplet
# Run this on the droplet after initial setup

set -e

echo "=== Micro Evals Deployment ==="

# Navigate to app directory
cd /opt/microevals/svelte-app

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Install dependencies
echo "Installing dependencies..."
npm ci --production=false

# Run database migrations
echo "Running database migrations..."
npm run db:push

# Build the application
echo "Building application..."
npm run build

# Restart the application
echo "Restarting PM2 process..."
pm2 restart micro-evals || pm2 start ecosystem.config.cjs --env production

echo "=== Deployment complete ==="
pm2 status
