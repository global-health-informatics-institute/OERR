
## **1. Systemd Service Unit**

Create a file named `op-agent.service` in `/etc/systemd/system/`:

```ini
[Unit]
Description=Op-Agent System Maintenance Framework
After=network.target

[Service]
Type=simple
User=rasberry
WorkingDirectory=/home/rasberry/agent/
ExecStart=/home/rasberry/agent/op_agent.sh
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
```

### **Explanation:**
- **`User=rasberry`**: Runs the service as the `rasberry` user.
- **`WorkingDirectory`**: Sets the working directory to `/home/rasberry/agent/`.
- **`ExecStart`**: **Full path** to the script (`/home/rasberry/agent/op_agent.sh`).
- **`Restart=on-failure`**: Automatically restarts the service if it crashes.
- **`StandardOutput/StandardError=journal`**: Logs output to the journal for debugging.
- **`Environment=PATH`**: Ensures the service has access to system binaries.

---

## **2. Systemd Timer Unit**

Create a file named `op-agent.timer` in `/etc/systemd/system/`:

```ini
[Unit]
Description=Run Op-Agent every 20 minutes

[Timer]
OnCalendar=*-*-* *:0/20:00
Persistent=true
Unit=op-agent.service

[Install]
WantedBy=timers.target
```

### **Explanation:**
- **`OnCalendar=*-*-* *:0/20:00`**: Triggers the timer every 20 minutes.
- **`Persistent=true`**: Runs missed executions at the next boot.
- **`Unit=op-agent.service`**: Specifies which service to trigger.

---

## **3. Enable and Start the Service and Timer**

1. **Reload systemd** to recognize the new units:
   ```bash
   sudo systemctl daemon-reload
   ```

2. **Enable the timer** to start at boot:
   ```bash
   sudo systemctl enable op-agent.timer
   ```

3. **Start the timer** immediately:
   ```bash
   sudo systemctl start op-agent.timer
   ```

4. **Verify the timer is active**:
   ```bash
   systemctl list-timers | grep op-agent
   ```

5. **Check the service status**:
   ```bash
   sudo systemctl status op-agent.service
   ```

---

## **4. Debugging and Logs**

- **View logs** for the service:
  ```bash
  journalctl -u op-agent.service -f
  ```

- **Manually trigger the service** (for testing):
  ```bash
  sudo systemctl start op-agent.service
  ```

---

## **Troubleshooting**
- If the service fails, check logs with `journalctl -u op-agent.service`.
- Ensure all scripts in `tasks/` are executable (`chmod +x tasks/*`).
- Ensure the `op_agent.sh` script is executable:
  ```bash
  chmod +x /home/rasberry/agent/op_agent.sh
  ```

---

## **Summary**
- The **service unit** defines how `op-agent` runs.
- The **timer unit** schedules it to run every 20 minutes.
- Use `systemctl` to manage the service and timer.
- Logs are available via `journalctl`.