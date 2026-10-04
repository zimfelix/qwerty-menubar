#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'Building the app requires macOS.' >&2
  exit 1
fi
PYTHON="${PYTHON:-python3}"
if [[ ! -x .venv/bin/python ]]; then
  "$PYTHON" -m venv .venv
fi
.venv/bin/python -m pip install -r requirements-build.txt
# These directories contain generated files only.
rm -rf build dist
.venv/bin/python setup.py py2app > /tmp/qwerty-menubar-build.log 2>&1 || {
  tail -n 80 /tmp/qwerty-menubar-build.log >&2
  exit 1
}
APP='dist/QWERTY Menu Bar.app'
if [[ -d dist/run.app && ! -e "$APP" ]]; then
  mv dist/run.app "$APP"
fi
/usr/libexec/PlistBuddy -c 'Delete :PythonInfoDict:PythonExecutable' "$APP/Contents/Info.plist"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"
ARCH="$(uname -m)"
ZIP="dist/QWERTY-Menu-Bar-macOS-${ARCH}.zip"
ditto -c -k --sequesterRsrc --keepParent "$APP" "$ZIP"
(cd dist && shasum -a 256 "$(basename "$ZIP")" > "$(basename "$ZIP").sha256")
echo "Built $APP and $ZIP"
