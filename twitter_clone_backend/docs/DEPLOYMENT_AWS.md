# AWS EC2 Production Deployment Guide

Guide for deploying the Twitter Clone Backend to an AWS EC2 instance using Docker Compose and Nginx.

## 1. Launch EC2 Instance

1. Launch an Ubuntu 24.04 LTS EC2 instance (`t3.medium` recommended).
2. Configure Security Group:
   - Allow Port 22 (SSH)
   - Allow Port 80 (HTTP)
   - Allow Port 443 (HTTPS)

## 2. Install Docker & Docker Compose on EC2

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2 git

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

## 3. Clone Repository & Setup Environment

```bash
git clone https://github.com/your-username/twitter_clone_backend.git
cd twitter_clone_backend

cp .env.production .env
```

Edit `.env` with production database credentials and strong secret keys:

```bash
nano .env
```

## 4. Run Production Containers

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## 5. Run Database Migrations

```bash
docker compose -f docker-compose.prod.yml exec web flask db upgrade
```

## 6. SSL Certificate via Certbot (HTTPS)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Verify status at `https://yourdomain.com/api/v1/health`.
