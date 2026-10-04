# QWERTY Menu Bar

Small Python/macOS menu-bar app that displays a static QWERTY keyboard reference.

- Communicate with Felix in German; use English code identifiers.
- Keep the runtime native AppKit/PyObjC: no web view, polling or network calls. The requested settings feature uses opt-in SMAppService login items and Carbon hotkeys, not an all-key event tap.
- Keep image processing and packaging dependencies out of the runtime imports.
- Check `git status` before changes. Do not overwrite unrelated changes.
- Verify pure logic with pytest, then verify the actual packaged `.app` on macOS. Distinguish automated checks from manual UI evidence and resource measurements.
- Felix explicitly requested public visibility after the settings update. The supplied Logitech photograph still has unverified redistribution rights: keep the MIT exclusion and do not claim ownership or redistribution permission.
- Hotkey validation must report its limits: macOS exposes system shortcuts and exclusive conflicts, not every shared/global/app-local shortcut. Never permanently suppress another app's shared registration.
- Deinstallation requires confirmation, validates the current own bundle and uses Trash. Never delete the source repository, Python's bundle or unrelated preference/cache files.
- Do not change the sibling `learning-sandbox` project or global agent instructions.
- Commit/push/release only when requested. The initial delivery explicitly includes a new GitHub repository and installable app.
