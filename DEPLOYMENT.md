# Deployment Guide for EC2

This guide explains how to deploy the Economic Letter Insights application on an AWS EC2 instance.

## Prerequisites

- AWS EC2 instance (Amazon Linux 2 or Ubuntu recommended)
- IAM role attached to EC2 with Bedrock access
- Python 3.11+ installed
- UV package manager installed
- Security group allowing inbound traffic on port 8000 (or your chosen port)

## EC2 Setup

### 1. Launch EC2 Instance

1. Launch an EC2 instance (t3.medium or larger recommended)
2. Attach an IAM role with the following permissions:
   - `bedrock:InvokeModel`
   - `bedrock:InvokeModelWithResponseStream`
3. Configure security group to allow:
   - SSH (port 22) from your IP
   - HTTP (port 8000) from desired IPs or 0.0.0.0/0 for public access

### 2. Connect to EC2

```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
```

### 3. Install Dependencies

#### For Amazon Linux 2 / Amazon Linux 2023:

```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install python3.11 -y

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

#### For Ubuntu:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv -y

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### 4. Clone and Setup Application

```bash
# Clone repository (or upload files)
git clone <your-repo-url>
cd frbsf-economic-letters-by-kiro

# Or if uploading manually:
# scp -i your-key.pem -r ./* ec2-user@your-ec2-ip:~/app/

# Install dependencies
uv sync
```

### 5. Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

Update the `.env` file:
```
AWS_DEFAULT_PROFILE=aws-admin-profile
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
DATABASE_PATH=./data/letters.db
HOST=0.0.0.0
PORT=8000
DEBUG=false
FRBSF_BASE_URL=https://www.frbsf.org/research-and-insights/publications/economic-letter/
SCRAPE_TIMEOUT=30
MAX_RETRIES=3
```

### 6. Test the Application

```bash
# Run the application
uv run python run.py
```

Access the application at: `http://your-ec2-ip:8000`

If it works, press Ctrl+C to stop it and proceed to setup as a service.

## Running as a System Service

### Create Systemd Service

1. Create service file:

```bash
sudo nano /etc/systemd/system/economic-letters.service
```

2. Add the following content:

```ini
[Unit]
Description=Economic Letter Insights Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/frbsf-economic-letters-by-kiro
Environment="PATH=/home/ec2-user/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ec2-user/.cargo/bin/uv run python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable economic-letters

# Start the service
sudo systemctl start economic-letters

# Check status
sudo systemctl status economic-letters
```

### Service Management Commands

```bash
# Start service
sudo systemctl start economic-letters

# Stop service
sudo systemctl stop economic-letters

# Restart service
sudo systemctl restart economic-letters

# View logs
sudo journalctl -u economic-letters -f

# View recent logs
sudo journalctl -u economic-letters -n 100
```

## Using Nginx as Reverse Proxy (Optional)

For production, it's recommended to use Nginx as a reverse proxy:

### 1. Install Nginx

```bash
# Amazon Linux
sudo yum install nginx -y

# Ubuntu
sudo apt install nginx -y
```

### 2. Configure Nginx

```bash
sudo nano /etc/nginx/conf.d/economic-letters.conf
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Start Nginx

```bash
# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Test configuration
sudo nginx -t

# Reload if needed
sudo systemctl reload nginx
```

Now access the application at: `http://your-ec2-ip` (port 80)

## SSL/HTTPS Setup (Optional)

### Using Let's Encrypt (Free SSL)

1. Install Certbot:

```bash
# Amazon Linux
sudo yum install certbot python3-certbot-nginx -y

# Ubuntu
sudo apt install certbot python3-certbot-nginx -y
```

2. Get SSL certificate:

```bash
sudo certbot --nginx -d your-domain.com
```

3. Auto-renewal is configured automatically. Test it:

```bash
sudo certbot renew --dry-run
```

## Monitoring and Maintenance

### View Application Logs

```bash
# Real-time logs
sudo journalctl -u economic-letters -f

# Last 100 lines
sudo journalctl -u economic-letters -n 100

# Logs from today
sudo journalctl -u economic-letters --since today
```

### Database Backup

```bash
# Create backup script
nano ~/backup-db.sh
```

Add:

```bash
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
cp ~/frbsf-economic-letters-by-kiro/data/letters.db $BACKUP_DIR/letters_$DATE.db
# Keep only last 7 days of backups
find $BACKUP_DIR -name "letters_*.db" -mtime +7 -delete
```

Make executable and add to crontab:

```bash
chmod +x ~/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /home/ec2-user/backup-db.sh
```

### Update Application

```bash
# Stop service
sudo systemctl stop economic-letters

# Pull latest changes
cd ~/frbsf-economic-letters-by-kiro
git pull

# Update dependencies
uv sync

# Start service
sudo systemctl start economic-letters
```

## Security Considerations

1. **Firewall**: Only allow necessary ports
   ```bash
   # Example using firewalld (Amazon Linux)
   sudo firewall-cmd --permanent --add-port=8000/tcp
   sudo firewall-cmd --reload
   ```

2. **IAM Role**: Use least privilege principle for EC2 IAM role

3. **Environment Variables**: Never commit `.env` to version control

4. **Database**: Regular backups and restrict file permissions
   ```bash
   chmod 600 ~/frbsf-economic-letters-by-kiro/data/letters.db
   ```

5. **Updates**: Keep system and dependencies updated
   ```bash
   sudo yum update -y  # Amazon Linux
   sudo apt update && sudo apt upgrade -y  # Ubuntu
   ```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status economic-letters

# Check logs
sudo journalctl -u economic-letters -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

### AWS Bedrock Access Issues

```bash
# Verify IAM role is attached
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Database Issues

```bash
# Check database file exists and permissions
ls -la ~/frbsf-economic-letters-by-kiro/data/

# Recreate database (will lose data)
rm ~/frbsf-economic-letters-by-kiro/data/letters.db
sudo systemctl restart economic-letters
```

## Performance Tuning

For high traffic:

1. **Increase EC2 instance size** (t3.large or larger)
2. **Use Gunicorn** instead of Uvicorn:
   ```bash
   uv add gunicorn
   # Update service ExecStart to:
   # ExecStart=/home/ec2-user/.cargo/bin/uv run gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```
3. **Enable caching** in Nginx
4. **Use RDS** instead of SQLite for better concurrency

## Cost Optimization

- Use **t3.micro** or **t3.small** for development/testing
- Use **t3.medium** for production with moderate traffic
- Enable **EC2 Auto Scaling** for variable traffic
- Use **Spot Instances** for non-critical environments
- Monitor **Bedrock costs** and implement rate limiting if needed
