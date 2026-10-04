"""Regular Python packaging, plus an opt-in self-contained .app build."""

import sys
import tomllib
from pathlib import Path
from sysconfig import get_config_var

from setuptools import setup

if "py2app" not in sys.argv:
    setup()  # Standard pip builds take their metadata from pyproject.toml.
else:
    from py2app.build_app import py2app

    class StandaloneApp(py2app):
        def finalize_options(self):
            # Dependencies are already installed from requirements-build.txt.
            # py2app rejects setuptools' dependency-resolution metadata.
            self.distribution.install_requires = []
            super().finalize_options()

    project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
    assets = list(map(str, Path("qwerty_menubar/assets").glob("*")))
    target = tuple(map(int, (get_config_var("MACOSX_DEPLOYMENT_TARGET") or "12.0").split(".")))
    minimum_macos = ".".join(map(str, max((12, 0), target)))
    setup(
        cmdclass={"py2app": StandaloneApp},
        app=["run.py"],
        data_files=[("assets", assets)],
        options={
            "py2app": {
                "argv_emulation": False,
                "iconfile": "qwerty_menubar/assets/app-icon.icns",
                "packages": ["qwerty_menubar"],
                "excludes": ["PIL", "pytest", "ruff", "tkinter", "test", "unittest"],
                "plist": {
                    "CFBundleName": "QWERTY Menu Bar",
                    "CFBundleDisplayName": "QWERTY Menu Bar",
                    "CFBundleIdentifier": "dev.zimfelix.qwerty-menubar",
                    "CFBundleShortVersionString": project["version"],
                    "CFBundleVersion": project["version"],
                    "LSUIElement": True,
                    "LSMultipleInstancesProhibited": True,
                    "LSMinimumSystemVersion": minimum_macos,
                    "NSHumanReadableCopyright": "Copyright © 2026 Felix Zimmermann",
                    "NSHighResolutionCapable": True,
                    "NSPrincipalClass": "NSApplication",
                },
            }
        },
    )
