#!/bin/bash

# --- AWS Low-Cost Deployment Script ---
# This script installs PostgreSQL, Nginx, and Python dependencies on a single EC2 instance.

echo "🚀 Starting Low-Cost AWS Setup..."

# 1. Update System
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Dependencies
sudo apt-get install -y python3-pip python3-venv nginx postgresql postgresql-contrib libpq-dev libgl1-mesa-glx

# 3. Setup SWAP (Crucial for t3.micro/1GB RAM)
echo "🛠 Setting up SWAP memory to prevent AI crashes..."
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Setup Database
echo "🐘 Configuring Local PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE kitchen_db;"
sudo -u postgres psql -c "CREATE USER kitchen_user WITH PASSWORD 'secure_password_123';"
sudo -u postgres psql -c "ALTER ROLE kitchen_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE kitchen_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE kitchen_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kitchen_db TO kitchen_user;"

# 5. Setup Project Folder
echo "📂 Setting up Project..."
cd /home/ubuntu
# (Assume the code is already cloned or uploaded here)
# python3 -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt

echo "✅ Setup Complete!"
echo "------------------------------------------------"
echo "Next Steps:"
echo "1. Update your .env file with DB_NAME=kitchen_db, DB_USER=kitchen_user, DB_PASSWORD=secure_password_123, DB_HOST=localhost"
echo "2. Run: python manage.py migrate"
echo "3. Run: gunicorn RateMyKitchen.wsgi"
echo "------------------------------------------------"
