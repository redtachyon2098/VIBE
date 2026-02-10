#!/bin/bash
set -euo pipefail

SESSION_NAME="VIBE"

# Read first two non-empty lines from sessionconfig.txt
mapfile -t COMMANDS < <(grep -v '^[[:space:]]*$' sessionconfig.txt)

AGENT_CMD="${COMMANDS[0]}"
CRITIC_CMD="${COMMANDS[1]}"

chmod +x setup.sh
./setup.sh

screen -dmS "$SESSION_NAME"

screen -S "$SESSION_NAME" -X screen -t Agent bash -il "
source bin/activate
$AGENT_CMD
"

screen -S "$SESSION_NAME" -X screen -t Critic bash -il "
source bin/activate
$CRITIC_CMD
"

screen -S "$SESSION_NAME" -X screen -t Monitor bash -il "
source bin/activate
exec bash
"

echo "Screen session '$SESSION_NAME' started."
echo "Attach with: screen -r $SESSION_NAME"
