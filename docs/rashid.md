- [Server Commands](#server-commands)

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

1. 
