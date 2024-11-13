- [Server Commands](#server-commands)
- [Cartop Commands](#cartop-commands)

## Server Commands
1. To list all timers running in the server
   ```bash
   systemctl list-timers --all
   ```
   - it will output the following:
     - next `date and time` the task is going to run
     - time left
     - last time it ran
     - the time passed since it ran
     - the name
     - and which service it is triggering

1. To check for **archiving**
   ```bash
   systemctl status task-archive.timer
   ```

1. To check for **Synchrozing**
   ```bash
   systemctl status task-sync.timer
   ```
   or
   ```bash
   systemctl status task-synchronization.timer
   ```

1. To check for the rest of **low priority tasks**
   ```bash
   sytemctl status task-resolve_conflicts.timer # to check if conflicts are actually being resolved
   system status task-clear_logs.timer # to check if log files are being removed in the server
   ```
- All commands above will a green or a white dot to indicate that there is no problem
- each timer will show you the time the script last ran and the next time (minutes) it will run

## Cartop Commands
1. To list all timers running in the carttop
   ```bash
   systemctl list-timers --all
   ```
   - it will output the following:
     - next `date and time` the task is going to run
     - time left
     - last time it ran
     - the time passed since it ran
     - the name
     - and which service it is triggering
  - The cartop is expected to display the following tasks:
    - _task-archive replication.timer_
    - _task-resolve conflicts.timer_ 
    - _task-resolve conflicts.timer_ 
    - _task-clearlog.timer_
    - _task-restart replication.timer_


1. To check for **archiving**
   ```bash
   systemctl status task-archive.timer
   ```

1. To check for **Synchrozing**
   ```bash
   systemctl status task-sync.timer
   ```
   or
   ```bash
   systemctl status task-synchronization.timer
   ```

1. To check for the rest of **low priority tasks**
   ```bash
   sytemctl status task-resolve_conflicts.timer # to check if conflicts are actually being resolved
   system status task-clear_logs.timer # to check if log files are being removed in the server
   system status task-restart_replication.timer # to check the activity of ensuring the replication is happening
   ```
- All commands above will a green or a white dot to indicate that there is no problem && time it is expected to run