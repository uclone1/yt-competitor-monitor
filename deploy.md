# Hostinger KVM2 Deployment — Complete Beginner Guide

Your code is on GitHub: **https://github.com/uclone1/yt-competitor-monitor**

This guide assumes **zero technical knowledge**. Follow each step exactly.

---

## PART 1: Connect to Your VPS Terminal

### Step 1: Open the Hostinger Terminal
1. Log in to **https://hpanel.hostinger.com**
2. Go to **VPS** → Click on your VPS
3. Look for **"Terminal"** or **"SSH Access"** button and click it
4. You should see a black screen with a blinking cursor — that's the terminal!

> **Alternative:** If you can't find the terminal button, download **PuTTY** from https://putty.org, enter your VPS IP, and connect with username `root` and your VPS password.

---

## PART 2: Install Everything & Download from GitHub (Copy-Paste Commands)

Copy **one line at a time**, paste it into the terminal, and press **Enter**. Wait for each to finish before pasting the next one.

### Step 2: Install Python & Git
```
sudo apt update
```
*(Wait 10-20 seconds)*

```
sudo apt install python3 python3-pip python3-venv git -y
```
*(Wait 30-60 seconds)*

### Step 3: Download your code from GitHub
```
git clone https://github.com/uclone1/yt-competitor-monitor.git /opt/yt-monitor
```

### Step 4: Set up Python and install dependencies
```
cd /opt/yt-monitor
```

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
pip install requests python-dotenv
```

### Step 5: Create the secrets file
```
cp .env.example .env
```

```
nano .env
```

A text editor will open. **Delete the placeholder text** and type this exactly:

```
SCRAPINGDOG_API_KEY=6997f4ab33974ac51862de44
GMAIL_ADDRESS=moharoon123@gmail.com
GMAIL_APP_PASSWORD=byif yuzt bykh cglw
RECIPIENT_EMAIL=moharoon123@gmail.com
```

Then press **Ctrl + O** → **Enter** to save, then **Ctrl + X** to exit.

---

## PART 3: Test It Works!

### Step 6: Run the automation manually
```
cd /opt/yt-monitor && source venv/bin/activate && python3 main.py
```

Wait about **2 minutes**. You should see:
```
[START] YouTube Competitor Monitor - Starting
[STEP 1] Fetching competitor channel data...
[OK] Fetched 15 channels...
[DONE] Report emailed successfully!
```

**Check your email** — you should receive the report!

---

## PART 4: Make It Run Every Day at 1 PM Automatically

### Step 7: Set your VPS timezone to IST
```
sudo timedatectl set-timezone Asia/Kolkata
```

### Step 8: Set up the daily schedule
```
crontab -e
```

If it asks you to choose an editor, **type `1`** and press Enter.

Go to the **very bottom** of the file and add this line:
```
0 13 * * * cd /opt/yt-monitor && /opt/yt-monitor/venv/bin/python3 /opt/yt-monitor/main.py >> /opt/yt-monitor/cron.log 2>&1
```

Press **Ctrl + O** → **Enter** to save, then **Ctrl + X** to exit.

### Step 9: Verify the schedule
```
crontab -l
```
You should see the line you just added.

---

## YOU'RE DONE! 🎉

The automation will now run **every day at 1 PM IST** and email you outperforming competitor videos.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "command not found" | Make sure you typed the command exactly as shown |
| No email received | Run: `cat /opt/yt-monitor/cron.log` to see errors |
| API errors | Check your ScrapingDog credit balance at scrapingdog.com |
| Gmail auth failed | Run `nano /opt/yt-monitor/.env` and check the App Password |
| Want to update the code | Run: `cd /opt/yt-monitor && git pull` |
