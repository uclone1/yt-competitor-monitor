# Deploying to Hostinger KVM2

## Prerequisites
- Hostinger KVM2 VPS with SSH access
- Python 3.9+ installed on the VPS

## Step-by-step Deployment

### 1. SSH into your VPS
```bash
ssh root@YOUR_VPS_IP
```

### 2. Install Python (if not present)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

# CentOS/RHEL
sudo yum install python3 python3-pip -y
```

### 3. Upload the project
```bash
mkdir -p /opt/yt-monitor
# Upload files via SCP or SFTP
scp -r ./* root@YOUR_VPS_IP:/opt/yt-monitor/
```

### 4. Set up virtual environment & install dependencies
```bash
cd /opt/yt-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure secrets
Edit `/opt/yt-monitor/.env` with your actual credentials (already configured).

### 6. Test manually
```bash
cd /opt/yt-monitor
source venv/bin/activate
python3 main.py
```

### 7. Set up cron job (1 PM IST = 7:30 AM UTC)
```bash
crontab -e
```
Add this line:
```
30 7 * * * cd /opt/yt-monitor && /opt/yt-monitor/venv/bin/python3 main.py >> /var/log/yt-monitor.log 2>&1
```

> **Note:** 1:00 PM IST = 7:30 AM UTC. Adjust if your VPS timezone is different.
> To check your VPS timezone: `timedatectl`
> If your VPS is set to IST, use `0 13 * * *` instead.

### 8. Verify cron is running
```bash
# Check cron logs next day
tail -f /var/log/yt-monitor.log
```

## Troubleshooting
- **No email received?** Check `automation.log` in the project directory for error details
- **API errors?** Verify your ScrapingDog API key and credit balance at scrapingdog.com
- **Gmail auth failed?** Make sure you're using an App Password, not your regular password
