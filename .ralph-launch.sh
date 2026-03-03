#!/bin/bash
set -uo pipefail
export PATH=/home/jeff/.npm-global/bin:$PATH
unset ANTHROPIC_API_KEY
cd /home/jeff/projects/worktrees/noxaudit-87
claude -p "$(cat /home/jeff/projects/worktrees/noxaudit-87/.ralph-prompt.txt)" --model claude-haiku-4-5 --dangerously-skip-permissions
code=$?
echo ""
echo "Ralph exited with code: $code"
echo "Session closes in 5 minutes. Press Enter to close now."
read -t 300 || true
