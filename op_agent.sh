#!/bin/bash

# Configuration
AGENT_DIR=$(pwd)
CONFIG_FILE="$AGENT_DIR/agent.conf"
TASKS_DIR="$AGENT_DIR/tasks"
LOGS_DIR="$AGENT_DIR/logs"

# ensure dirs & config file exist
mkdir -p "$TASKS_DIR" "$LOGS_DIR"
touch "$CONFIG_FILE"


# ensure the scripts are executable
chmod +x "$TASKS_DIR"/*


# Get current time in HHMM (e.g., 0405)
NOW_HHMM=$(date +%H%M)
# Convert current time to total minutes for grace window math
NOW_MINS=$((10#${NOW_HHMM:0:2} * 60 + 10#${NOW_HHMM:2:2}))


echo "--- Op-Agent Execution: $(date) ---"

grep "<<op:" "$CONFIG_FILE" | while read -r line; do
    # Extract script name and window string
    SCRIPT=$(echo "$line" | sed -n "s/.*op:[\`']\([^'\`]*\)[\`'].*/\1/p")
    WINDOW_STR=$(echo "$line" | sed -n "s/.*window:[\`]\([^>]*\)[\`].*/\1/p" | tr -d '` ')

    SHOULD_RUN=false

    # 1. Handle Anytime (*)
    if [[ "$WINDOW_STR" == "*" ]]; then
        SHOULD_RUN=true
    else
        # 2. Handle specific HHMM windows with 15-min grace logic
        # Split window string into 4-character chunks
        for (( i=0; i<${#WINDOW_STR}; i+=4 )); do
            TARGET_HHMM=${WINDOW_STR:i:4}
            [ -z "$TARGET_HHMM" ] && continue
            
            # Convert target window to total minutes
            TARGET_MINS=$((10#${TARGET_HHMM:0:2} * 60 + 10#${TARGET_HHMM:2:2}))
            
            # Calculate difference
            DIFF=$(( NOW_MINS - TARGET_MINS ))
            # Absolute value
            ABS_DIFF=${DIFF#-}

            if [ "$ABS_DIFF" -le 15 ]; then
                SHOULD_RUN=true
                break
            fi
        done
    fi

    # 3. Execution with Crash Protection
    if [ "$SHOULD_RUN" = true ]; then
        if [ -f "$TASKS_DIR/$SCRIPT" ]; then
            echo "[RUNNING] $SCRIPT"
            # Run in subshell so a 'set -e' or crash in OP doesn't stop the runner
            (
                export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
                cd "$TASKS_DIR" || exit
                ./"$SCRIPT"
            )
            if [ $? -ne 0 ]; then
                echo "[FAILED] $SCRIPT exited with non-zero status. Skipping to next OP."
            fi
        else
            echo "[MISSING] $SCRIPT not found in $TASKS_DIR"
        fi
    else
        echo "[SKIPPED] $SCRIPT (Outside 15m grace window)"
    fi
done
