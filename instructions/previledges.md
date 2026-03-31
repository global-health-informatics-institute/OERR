# Privileges and Sudo Rules for Op-Agent

This document outlines the constraints and requirements for granting elevated privileges to Op-Agent scripts. It also lists all commands that require root access and how to configure them securely.

---

## **Privilege Constraints**

1. **Minimal Privileges:**
   - Only grant `sudo` access to the **minimal set of commands** required for your OPs (scripts in `tasks/`).
   - Avoid granting `sudo` access to shells (`/bin/bash`, `/bin/sh`) or broad commands.

2. **Absolute Paths:**
   - Always use **absolute paths** for commands in `/etc/sudoers.d/op-agent`.

3. **No Wildcards:**
   - Avoid using wildcards (`*`) unless absolutely necessary. If used, restrict them to command arguments, not the command itself.

4. **Passwordless Sudo:**
   - Use `NOPASSWD` to allow OPs to run without manual password input.

---

## **Setting Up Sudo Rules**

To allow specific commands to run with root privileges, add entries to the `/etc/sudoers.d/op-agent` file. Use the following format for each entry:

```ini
pi ALL=(root) NOPASSWD: /path/to/command
```

### **Example Entries**

Here are common commands that may require root access:

```ini
pi ALL=(root) NOPASSWD: /usr/bin/apt-get          # Package management
pi ALL=(root) NOPASSWD: /usr/bin/apt              # Package management (alternative)
pi ALL=(root) NOPASSWD: /bin/systemctl            # Service management
pi ALL=(root) NOPASSWD: /usr/bin/journalctl        # Log access
pi ALL=(root) NOPASSWD: /bin/chmod                # File permission changes
pi ALL=(root) NOPASSWD: /bin/chown                # File ownership changes
pi ALL=(root) NOPASSWD: /sbin/reboot              # System reboot
pi ALL=(root) NOPASSWD: /sbin/shutdown            # System shutdown
pi ALL=(root) NOPASSWD: /home/pi/Desktop/GHII/op-agent/tasks/op_example.sh  # Custom OP script
```

---

## **How to Apply the Rules**

1. **Create the Sudoers File:**
   ```bash
   sudo nano /etc/sudoers.d/op-agent
   ```

2. **Add the Entries:**
   Paste the required entries (as shown above) into the file.

3. **Set Correct Permissions:**
   ```bash
   sudo chmod 0440 /etc/sudoers.d/op-agent
   ```

4. **Validate the File:**
   ```bash
   sudo visudo -c
   ```

---

## **Security Best Practices**

- **Never** allow `/bin/bash` or `/bin/sh` with `NOPASSWD`.
- **Test** your OPs to ensure they run as expected:
  ```bash
  sudo journalctl -u op-agent.service -f
  ```
- **Audit** the `/etc/sudoers.d/op-agent` file regularly to ensure no unnecessary privileges are granted.

---

## **Troubleshooting**

- If an OP fails, check the logs:
  ```bash
  journalctl -u op-agent.service
  ```
- Manually test an OP:
  ```bash
  sudo /home/pi/Desktop/GHII/op-agent/op_agent.sh
  ```

---

## **Notes**

- Replace `/home/pi/Desktop/GHII/op-agent/tasks/op_example.sh` with the actual path to any OP script that needs `sudo`.
- Ensure all scripts in `tasks/` are executable:
  ```bash
  chmod +x /home/pi/Desktop/GHII/op-agent/tasks/*
  ```
```