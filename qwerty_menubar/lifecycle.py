"""Guarded login-item and uninstall integration. Never remove the source project."""

import plistlib
from pathlib import Path

from qwerty_menubar.constants import BUNDLE_ID


class LifecycleError(ValueError):
    pass


def installed_bundle(path, identifier):
    """Only accept this application's own real, packaged bundle."""
    bundle = Path(path)
    if identifier != BUNDLE_ID or bundle.suffix != ".app" or bundle.is_symlink():
        raise LifecycleError("Nur in der installierten QWERTY Menu Bar.app verfügbar.")
    try:
        info = plistlib.loads((bundle / "Contents" / "Info.plist").read_bytes())
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        raise LifecycleError("Ungültiges App-Bundle.") from error
    if info.get("CFBundleIdentifier") != BUNDLE_ID:
        raise LifecycleError("Diese Anwendung darf nicht entfernt werden.")
    if not (bundle / "Contents" / "MacOS" / info.get("CFBundleExecutable", "")).is_file():
        raise LifecycleError("App-Programm nicht gefunden.")
    return bundle


class LoginItem:
    def __init__(self, bundle_path, identifier, service=None):
        self.bundle_path, self.identifier = bundle_path, identifier
        if service is None:
            from ServiceManagement import SMAppService

            service = SMAppService.mainAppService()
        self.service = service

    def status(self):
        try:
            installed_bundle(self.bundle_path, self.identifier)
        except LifecycleError:
            return 3  # source checkout / invalid bundle
        return self.service.status()

    def set_enabled(self, enabled):
        installed_bundle(self.bundle_path, self.identifier)
        method = (
            self.service.registerAndReturnError_
            if enabled
            else self.service.unregisterAndReturnError_
        )
        success, error = method(None)
        if not success:
            detail = error.localizedDescription() if error else "Unbekannter macOS-Fehler"
            raise LifecycleError(f"Autostart konnte nicht geändert werden: {detail}")
        return self.status()

    def open_settings(self):
        from ServiceManagement import SMAppService

        SMAppService.openSystemSettingsLoginItems()


def remove_preferences_and_lock(preferences, cache_dir):
    preferences.remove()
    cache_dir = Path(cache_dir)
    (cache_dir / "instance.lock").unlink(missing_ok=True)
    try:
        cache_dir.rmdir()
    except OSError:
        pass  # never recursively remove unrelated files
