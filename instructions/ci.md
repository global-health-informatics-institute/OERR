
# Distributed Kiosk Git Sync Guide (LAN Only)

This guide provides the finalized synchronization pipeline for an air-gapped network, utilizing **systemd** on both the Ubuntu server and Raspberry Pi kiosks.

## Overview
This setup creates a local, high-speed **deployment pipeline** designed for stability and zero-touch updates.

- **The Hub (Ubuntu Server):** Runs `git-daemon` to share repositories over LAN on port 9418.
- **The Kiosks (Raspberry Pis):** Run a **systemd timer** that triggers a "Smart Sync" script every minute.
- **The Sync Logic:** Compares **Local Hash** vs **Remote Hash**. If they differ, it backs up specific configuration files, clears the Git index to bypass "not uptodate" errors, performs a forced update,

---

### 1. Create a Bare Repo
```bash
# server
cd bare_repo/home/ghii/bare_repos/
mkdir -p op-agent.bak
cd op-agent.bak
git init --bare


# push the op-agent branch
git remote add ci-op-agent <server-user>@<server-ip>:/home/ghii/bare_repos/op-agent.git
git push  ci-op-agent op-agent 

# cartop
# clone the op agent
```
---

### 2. Raspberry Pi: Automated Sync Service
The Pi uses a **systemd timer** for reliable, logged execution.

Create `/home/rasberry/ci_sync_kiosk.sh` on the Pi:

```bash
#!/bin/bash
REPO_PATH="/home/rasberry/op-agent"
BRANCH="op-agent"
REMOTE_URL="git://<server_ip>/op-agent.git"
REMOTE_NAME="ci-remote"
cd $REPO_PATH || exit

# 1. Ensure remote is set
if ! git remote | grep -q "$REMOTE_NAME"; then
    git remote add $REMOTE_NAME $REMOTE_URL
fi

# 2. Fetch changes
git fetch $REMOTE_NAME $BRANCH

# 3. Fix Permissions (Clears lockouts from previous runs)
sudo chown -R rasberry:rasberry .

# 4. Compare hashes
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse $REMOTE_NAME/$BRANCH)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "Update detected. Local: $LOCAL | Remote: $REMOTE"

    # 5. FORCE RESET (The Sledgehammer)
    git reset --hard $REMOTE_NAME/$BRANCH || {
        echo "Reset failed, forcing index clear..."
        rm -f .git/index
        git checkout -f $REMOTE_NAME/$BRANCH
    }

    git clean -fdx

    echo "Sync and Restore complete."
    sudo systemctl restart op-agent.service
else
    echo "Already up to date."
fi
```

Make executable:

```bash
chmod +x /home/rasberry/ci_sync_kiosk.sh
```

### 3. The Sync Service

Create `/etc/systemd/system/ci-kiosk-sync.service`:

```ini
[Unit]
Description=Kiosk Git Sync Execution
After=network.target

[Service]
Type=oneshot
User=rasberry
WorkingDirectory=/home/<rasberry>/op-agent
ExecStart=/home/rasberry/ci_sync_kiosk.sh
```

### 4. The Sync Timer

Create `/etc/systemd/system/ci-kiosk-sync.timer`:

```ini
[Unit]
Description=Trigger Kiosk Sync every on defined times

[Timer]
OnBootSec=1min
OnCalendar=*-*-* 00,08,12:00:00
OnCalendar=*-*-* 16:30:00
Persistent=true
Unit=kiosk-sync.service

[Install]
WantedBy=timers.target
```

### 5. Activate on Pi

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ci-kiosk-sync.timer
```
---