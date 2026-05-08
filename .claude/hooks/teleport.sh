#!/bin/bash
# Implements `claude --teleport <session-id>` by delegating to `claude --resume`.
#
# Usage:
#   ./teleport.sh <session-id>
#   claude --teleport <session-id>   (via shell alias)
set -euo pipefail

SESSION_ID="${1:-}"
if [ -z "$SESSION_ID" ]; then
  echo "Usage: $0 <session-id>" >&2
  exit 1
fi

if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found on PATH. Install it with: npm install -g @anthropic-ai/claude-code" >&2
  exit 1
fi

exec claude --resume "$SESSION_ID"
