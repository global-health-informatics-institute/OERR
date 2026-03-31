Op-Agent: System Maintenance Framework
Op-Agent is a local monitoring and maintenance suite designed for air-gapped Raspberry Pi (Ubuntu) environments. It uses a "swarm" of independent bash scripts (OPs) to ensure system health without external dependencies.
Directory Structure


```text
OERR/agent/
├── op_agent.sh        # The main runner (Execution Engine)
├── agent.conf         # The master configuration (Schedule & OPs)
├── tasks/             # Directory containing the OP scripts
│   ├── check_disk.sh
│   └── rotate_logs.sh
└── logs/              # Execution history
```


Adding a New OP (Operation)
To add a new task to the swarm, follow these two steps:
1. Create the Script
Place your bash script in the `/home/agent/tasks/` directory.
use snake case naming convention for scripts (e.g., check_disk.sh, rotate_logs.sh).


* Requirement: Ensure the script is executable: chmod +x tasks/your_script.sh
* Standard: Use absolute paths inside your script since it runs via a runner.
* Make sure the script does not require elevated permissions unless necessary.
  * if it does, create a NOPASSWD entry for that specific command to allow the OP to run without manual intervention.
* tasks can only run on a 4-hour schedule, so design your OPs to be efficient and complete within that window.
  * op_agent will compasate a grace window for OPs that are 15mins off configured schedule


1. Update the Config
Add a new line to agent.conf using the specific Op-Agent syntax:


<<op:`script_name.sh`,window:`time_codes`>>


Time Window Options:


| Window Type | Syntax | Description |
|---|---|---|
| Anytime | window:*`` | Runs every time the agent fires (every 4 hrs). |
| Single Time | window:0400`` | Runs only when the hour is 04:00. |
| Multiple Times | window:000004000800`` | Runs at 12AM, 4AM, and 8AM. |


------------------------------
Important Constraints & Rules


   1. HHMM Format: The window must use the 24-hour HHMM format (e.g., 1600 for 4 PM). Do not use colons.
   2. The Skip Logic: If the current system time does not match a time listed in the window, the script skips.
   3. No Internet: Use only native Ubuntu tools (grep, sed, awk, systemctl). Do not add dependencies that require apt install.
   4. Execution Window: The agent is triggered by a Systemd Timer every 4 hours. Ensure your window values align with the 4-hour intervals (e.g., 0000, 0400, 0800, etc.) or use * for every run.
   5. Leading Zeros: Always include leading zeros for hours (e.g., use 0800, not 800).
   6. op_agent will skip any op that crushes
   7. only the op_agent runner is executed by the systemd timer, not the individual OPs. This means that if an OP is scheduled to run at a specific time, it will only execute when the runner is triggered by the timer and the current time matches the OP's window.
   8. Depends on agent working directory being `path/to/root/agent`. Set systemd service to work in this dir


Troubleshooting


* View Agent Logs: journalctl -u op-agent.service
* Check Schedule: systemctl list-timers | grep op-agent
* Manual Run: To test current OPs immediately, run: sudo /opt/op-agent/op-agent.sh
