#!/bin/bash
set -euo pipefail

# Only run in Claude Code remote (web) sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# This is an AL (Business Central) extension project.
# AL compilation and deployment are handled by the AL Language VS Code extension.
# There are no runtime dependencies to install via a package manager.
echo "AL project ready. No package dependencies to install."
