# Entwicklung und Prüfungen

## Quellstart

Python 3.12+ und macOS 13+; der verwendete Python-Build kann eine neuere macOS-Version voraussetzen. Der angebotene Standalone-Download benötigt Apple Silicon und macOS 26+.

```bash
git clone https://github.com/zimfelix/qwerty-menubar.git
cd qwerty-menubar
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m qwerty_menubar
```

Autostart und Deinstallation sind im Quellstart deaktiviert: Weder der Python-Interpreter noch sein Bundle dürfen als Anmeldeobjekt eingerichtet oder entfernt werden. Hotkeys bleiben verfügbar; der Quellstart verwendet dieselbe Benutzer-Konfiguration wie die installierte App. Beide deshalb nicht parallel im Alltag betreiben.

## Standalone-App bauen und installieren

```bash
./scripts/build.sh
./scripts/install.sh
```

Erzeugt werden:

- `dist/QWERTY Menu Bar.app`
- `dist/QWERTY-Menu-Bar-macOS-arm64.zip` auf Apple Silicon
- die passende `.zip.sha256`-Datei

Python und Laufzeitbibliotheken sind gebündelt. Die `.app` benötigt weder Repository noch `.venv`. Der Build ist ad-hoc signiert, nicht notarisiert. Das Installationsskript aktiviert keinen Autostart und überschreibt keine bestehende App: Vor einem Update die alte App beenden und ihre Kopie verschieben.

Download optional prüfen: ZIP und SHA-256-Datei in denselben Ordner herunterladen, dort ausführen:

```bash
shasum -a 256 -c QWERTY-Menu-Bar-macOS-arm64.zip.sha256
```

Die Prüfsumme bestätigt die Übereinstimmung mit der heruntergeladenen Hash-Datei, nicht unabhängig die Vertrauenswürdigkeit des Herausgebers.

## Prüfen

```bash
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
bash -n scripts/build.sh scripts/install.sh
```

Optionale native Prüfungen auf einem angemeldeten Mac:

```bash
.venv/bin/python -m tools.check_hotkeys_macos
.venv/bin/python -m tools.check_settings_macos
.venv/bin/python -m tools.check_macos --display-id DISPLAY_ID --cycles 100 --idle-seconds 10
```

Sie verwenden temporäre Registrierungen und eigene Testeinstellungen; die Papierkorb-Prüfung verwendet nur eine temporäre App-Kopie. Kein Autostart wird eingerichtet und die Benutzer-App wird nicht entfernt. Vor sichtbaren Prüfungen den Desktop entsperren und die aktuelle Monitoranordnung überprüfen. Native Selektor-/API-Prüfungen ersetzen keine vollständigen Benutzerabläufe.

Ergebnisse und offene Nachweise: [VERIFICATION.md](VERIFICATION.md). GitHub Actions ist ausschließlich manuell auslösbar; Runner-Minuten können kostenpflichtig sein.

## Aufbau

```text
Menüleisten-Klick / Hotkey → AppKit-Popover → Tastaturbild + Zahnrad
                                                               ↓
                                                          Einstellungen
                                    ┌──────────────────────────┼──────────────┐
                                    ↓                          ↓              ↓
                               SMAppService             Hotkey + JSON      Papierkorb
                               Anmeldeobjekt            Konfliktprüfung    mit Bestätigung
```

- `app.py`, `ui_controls.py`: Menüleiste, Popover und neutraler Zahnrad-Button
- `settings.py`, `settings_ui.py`: Menü und lokaler Shortcut-Recorder
- `shortcuts.py`, `hotkeys.py`: Datenmodell, Standardkürzel, Konflikte und Carbon-Registrierung
- `preferences.py`, `lifecycle.py`: atomare JSON-Einstellungen, Login-Items und eigene Bundle-/Dateiprüfung
- `layout.py`, `assets/`: Größenberechnung, fertiges Tastaturbild und Icons
- `tools/prepare_image.py`: Bildvorbereitung; Pillow wird nicht zur Laufzeit importiert

Das fehlende Einstellungsfile bedeutet Standardkürzel `cmd+ctrl+shift+p`; ein gespeichertes `hotkey: null` bedeutet bewusst deaktiviert. Gespeicherte Kombinationen verwenden physische macOS-Keycodes. Nach dem Start werden Kombinationen erneut geprüft. Schreib-/Registrierungsfehler müssen die vorherige Belegung erhalten.
