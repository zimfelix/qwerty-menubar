# QWERTY Menu Bar

Small Python/macOS menu-bar app that displays a static QWERTY keyboard reference.

- Communicate with Felix in German; use English code identifiers.
- Keep the runtime native AppKit/PyObjC: no web view, polling, network calls, keyboard hooks, or login item without an explicit request.
- Keep image processing and packaging dependencies out of the runtime imports.
- Check `git status` before changes. Do not overwrite unrelated changes.
- Verify pure logic with pytest, then verify the actual packaged `.app` on macOS. Distinguish automated checks from manual UI evidence and resource measurements.
- The supplied Logitech photograph has unverified redistribution rights. Keep the repository/releases private unless Felix explicitly decides otherwise; do not claim ownership of the image.
- Do not change the sibling `learning-sandbox` project or global agent instructions.
- Commit/push/release only when requested. The initial delivery explicitly includes a new GitHub repository and installable app.
