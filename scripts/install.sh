#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
APP='dist/QWERTY Menu Bar.app'
DEST="$HOME/Applications/QWERTY Menu Bar.app"
if [[ ! -d "$APP" ]]; then
  ./scripts/build.sh
fi
if [[ -e "$DEST" ]]; then
  echo "Already installed: $DEST. Quit the app and move the old copy aside before updating." >&2
  exit 1
fi
mkdir -p "$HOME/Applications"
ditto "$APP" "$DEST"
open "$DEST"
echo "Installed $DEST (no login item or background service added)."
