import plistlib

import pytest

from qwerty_menubar.constants import BUNDLE_ID
from qwerty_menubar.lifecycle import (
    LifecycleError,
    LoginItem,
    installed_bundle,
    remove_preferences_and_lock,
)
from qwerty_menubar.preferences import Preferences


def make_bundle(tmp_path, identifier=BUNDLE_ID):
    bundle = tmp_path / "QWERTY Menu Bar.app"
    contents = bundle / "Contents"
    executable = contents / "MacOS" / "QWERTY Menu Bar"
    executable.parent.mkdir(parents=True)
    executable.write_text("test executable")
    (contents / "Info.plist").write_bytes(
        plistlib.dumps({"CFBundleIdentifier": identifier, "CFBundleExecutable": "QWERTY Menu Bar"})
    )
    return bundle


def test_only_own_packaged_bundle_is_accepted(tmp_path):
    bundle = make_bundle(tmp_path)
    assert installed_bundle(str(bundle), BUNDLE_ID) == bundle
    with pytest.raises(LifecycleError):
        installed_bundle(str(bundle), "org.python.python")
    with pytest.raises(LifecycleError):
        installed_bundle(str(tmp_path), BUNDLE_ID)
    alias = tmp_path / "alias.app"
    alias.symlink_to(bundle)
    with pytest.raises(LifecycleError):
        installed_bundle(str(alias), BUNDLE_ID)


def test_other_app_cannot_be_removed_even_with_claimed_identifier(tmp_path):
    bundle = make_bundle(tmp_path, "other.app")
    with pytest.raises(LifecycleError):
        installed_bundle(str(bundle), BUNDLE_ID)


class FakeService:
    def __init__(self):
        self.current, self.calls, self.fail = 0, [], False

    def status(self):
        return self.current

    def registerAndReturnError_(self, error):
        self.calls.append("register")
        if self.fail:
            return False, None
        self.current = 1
        return True, None

    def unregisterAndReturnError_(self, error):
        self.calls.append("unregister")
        self.current = 0
        return True, None


def test_login_toggle_uses_os_status_and_has_no_startup_side_effect(tmp_path):
    service = FakeService()
    item = LoginItem(str(make_bundle(tmp_path)), BUNDLE_ID, service)
    assert item.status() == 0
    assert service.calls == []
    assert item.set_enabled(True) == 1
    assert item.set_enabled(False) == 0
    assert service.calls == ["register", "unregister"]


def test_login_is_never_enabled_from_source_python(tmp_path):
    service = FakeService()
    item = LoginItem(str(tmp_path), "org.python.python", service)
    assert item.status() == 3
    with pytest.raises(LifecycleError):
        item.set_enabled(True)
    assert service.calls == []


def test_os_failure_is_visible_not_silently_marked_enabled(tmp_path):
    service = FakeService()
    service.fail = True
    item = LoginItem(str(make_bundle(tmp_path)), BUNDLE_ID, service)
    with pytest.raises(LifecycleError, match="Autostart"):
        item.set_enabled(True)
    assert item.status() == 0


def test_cleanup_only_removes_owned_files(tmp_path):
    preferences = Preferences(tmp_path / "preferences" / "settings.json")
    preferences.save_shortcut(None)
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "instance.lock").write_text("")
    (cache / "unrelated.txt").write_text("keep")
    source = tmp_path / "source.py"
    source.write_text("keep")
    remove_preferences_and_lock(preferences, cache)
    assert not preferences.path.exists()
    assert not (cache / "instance.lock").exists()
    assert (cache / "unrelated.txt").read_text() == "keep"
    assert source.read_text() == "keep"
