# QWERTY Menu Bar

Eine kleine **native Python-App für die macOS-Menüleiste**: Tastatur-Icon anklicken, QWERTY-Layout einer Logitech-Mini-Tastatur nachsehen, weiterarbeiten.

## Bedienung

- **Linksklick** auf das Menüleisten-Icon öffnet/schließt das freigestellte Tastaturbild.
- **Zahnrad oben rechts im Popover** öffnet das kleine Einstellungsmenü. Alternativ: Rechtsklick auf das Menüleisten-Icon.
- **Autostart · Aus/Ein:** native macOS-Anmeldeobjekte, standardmäßig aus. Bei notwendiger macOS-Freigabe zeigt das Menü den echten Status und einen Link zu den Systemeinstellungen.
- **Tastenkürzel:** Aufnahme per Tastendruck oder manuelle Eingabe, zum Beispiel `ctrl+alt+cmd+k` / `⌃⌥⌘K`. Das Kürzel blendet die Tastatur global ein/aus.
- **Beenden:** beendet nur die App; ein bewusst aktivierter Autostart bleibt für die nächste Anmeldung erhalten.
- **Deinstallieren …:** ausdrückliche Bestätigung, danach die laufende `.app` in den Papierkorb verschieben und eigenen Autostart, Hotkey und Einstellungen entfernen. Quellprojekt und GitHub-Repo bleiben unberührt. Abbrechen ist die sichere Standardaktion.

Kein Dock-Icon, kein Electron, kein Browser, keine Netzwerklogik und keine Polling-Timer. Ein bei Bedarf geladenes Bild wird wiederverwendet. Die App liest keine allgemeinen Tastatureingaben mit und benötigt keine Bedienungshilfen-/Input-Monitoring-Freigabe. Der Recorder verarbeitet Eingaben nur in seinem eigenen Fenster.

Die Tastatur ist eine **Layout-Referenz**, kein Remapping-Werkzeug. Die App ändert weder das Systemlayout noch bestehende Systemkürzel.

## Hotkeys und Konfliktprüfung

Vor dem Speichern werden geprüft:

1. Unterstützte Taste plus mindestens `⌘`, `⌃` oder `⌥`; zusätzliche Modifier wie `⇧` sind möglich. Reine Modifier/Fn allein werden nicht unterstützt.
2. Aktivierte macOS-Systemkürzel über `CopySymbolicHotKeys` — einschließlich Standardbelegungen, nicht nur Änderungen aus einer Preferences-Datei.
3. Konservativ reservierte übliche App-/Textkürzel, etwa `⌘C`, `⌘Q` und `⌘⇧Z`.
4. Konflikte mit exklusiv registrierten globalen Hotkeys über eine kurzzeitige Carbon-Registrierungsprüfung.

**Wichtige Grenze:** macOS stellt kein vollständiges Verzeichnis aller Kürzel anderer Apps bereit. Nicht-exklusive globale Registrierungen, Event-Tap-Hotkeys und app-interne Kürzel lassen sich nicht zuverlässig ausschließen. Die endgültige Registrierung ist deshalb **nicht exklusiv** und verdrängt keine vorhandene geteilte Registrierung. Vollständige Konfliktfreiheit wird nicht versprochen.

Wenn macOS oder eine andere App einen Tastendruck bereits abfängt, kann der lokale Recorder ihn nicht bekommen. Dafür gibt es das manuelle Eingabefeld. Manuelle Zeichennamen beziehen sich auf QWERTY-Tastenpositionen; die Aufnahme zeigt die Beschriftung des aktuellen Eingabelayouts. Die gespeicherte Kombination verwendet einen physischen macOS-Keycode.

Ein abgelehntes Kürzel oder fehlgeschlagenes Speichern lässt die bisherige Belegung unverändert. Einstellungen werden atomar in einer kleinen JSON-Datei gespeichert; nach Neustart wird ein gespeichertes Kürzel erneut geprüft. Gehaltene Tasten lösen keinen ständigen Ein-/Aus-Wechsel aus.

## Installation ohne Python

1. Im [Release v0.2.0](https://github.com/zimfelix/qwerty-menubar/releases/tag/v0.2.0) die macOS-ZIP herunterladen.
2. Entpacken und **QWERTY Menu Bar.app** nach `~/Applications` oder `/Applications` ziehen.
3. App öffnen. Das kleine Tastatur-Icon erscheint rechts in der Menüleiste.

Der hier erstellte Download benötigt **Apple Silicon (arm64) und macOS 26 oder neuer**. Python und Bibliotheken sind enthalten. Ein Internetzugang oder installiertes Python ist nach dem Download nicht nötig. Intel-/ältere-macOS-Builds wurden nicht geprüft.

```bash
gh release download v0.2.0 --repo zimfelix/qwerty-menubar --pattern '*.zip' --dir ~/Downloads
```

### Gatekeeper

Der Build ist **ad-hoc signiert, nicht mit einer Apple Developer ID signiert oder notarisiert**. Bei heruntergeladenen Builds kann macOS eine ausdrückliche Sicherheitsbestätigung verlangen: Öffnungsversuch, anschließend **Systemeinstellungen → Datenschutz & Sicherheit → Dennoch öffnen**, sofern angeboten. Nur für ein selbst gebautes oder vertrauenswürdiges Release bestätigen. Keine globale Gatekeeper-Abschaltung und kein automatisches Entfernen von Quarantäne-Attributen.

## Entwicklung

Quellcode benötigt Python 3.12+ und macOS 13+ (der konkrete Python-Build kann eine neuere macOS-Version voraussetzen):

```bash
git clone https://github.com/zimfelix/qwerty-menubar.git
cd qwerty-menubar
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m qwerty_menubar
```

Autostart und Deinstallation sind im Quellstart absichtlich deaktiviert: Die App darf weder den Python-Interpreter als Login-Item einrichten noch dessen Bundle entfernen.

```bash
./scripts/build.sh
./scripts/install.sh
```

Ergebnis: `dist/QWERTY Menu Bar.app`, ZIP und SHA-256-Datei. Die installierte App läuft unabhängig von Repository und `.venv`. Das Installationsskript richtet keinen Autostart ein. Vor Updates die App beenden und die alte Kopie verschieben; bestehende Installationen werden nicht ungefragt überschrieben.

## Prüfungen

```bash
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m tools.check_hotkeys_macos
.venv/bin/python -m tools.check_settings_macos
```

Native Prüfwerkzeuge verwenden vorübergehende Hotkey-Registrierungen bzw. eigene temporäre Einstellungen und eine temporäre App-Kopie. Sie aktivieren keinen Autostart und deinstallieren nicht die Benutzer-App.

Aktuelle Ergebnisse und klare Nachweisgrenzen stehen in [VERIFICATION.md](VERIFICATION.md). Sichtbare Tests benötigen einen entsperrten Desktop und einen bewusst gewählten Monitor. Die optionale GitHub-Actions-Prüfung ist nur manuell auslösbar; private macOS-Runner-Minuten können kostenpflichtig sein.

## Aufbau

```text
Menüleisten-Klick / globaler Hotkey → AppKit-Popover → PNG + Zahnrad
                                                           ↓
                                                     Settings-Menü
                                ┌──────────────────────────┼────────────────────┐
                                ↓                          ↓                    ↓
                         SMAppService               Hotkey-Prüfung        Papierkorb
                         Anmeldeobjekt              + JSON-Datei          nach Bestätigung
```

- `app.py`: Menüleisten-Icon, Popover und Ereignissteuerung
- `settings.py` / `settings_ui.py`: Einstellungsmenü und kompakter Recorder
- `shortcuts.py` / `hotkeys.py`: Datenmodell, Konfliktregeln und native Registrierung
- `preferences.py` / `lifecycle.py`: atomare Einstellungen, Login-Items und sichere Bundle-Prüfung
- `layout.py` / `assets/`: Größenberechnung, fertiges Bild und Icons
- `tools/`, `scripts/`, `tests/`: Bildvorbereitung, Build, Installation und Prüfungen

## Deinstallation / gespeicherte Dateien

Bevorzugt Zahnrad → **Deinstallieren …**. Die App liegt anschließend im Papierkorb. Das Quellprojekt bleibt bestehen.

Eigene Daten liegen unter:

- `~/Library/Application Support/dev.zimfelix.qwerty-menubar/settings.json`
- `~/Library/Caches/dev.zimfelix.qwerty-menubar/instance.lock`

Bei manueller Deinstallation vorher Autostart ausschalten oder das Anmeldeobjekt in macOS entfernen, App beenden und `.app` sowie optional diese eigenen Dateien löschen.

## Lizenz und Bildrechte

Der selbst erstellte Programmcode steht unter der MIT-Lizenz. Das bereitgestellte Logitech-Tastaturfoto (`qwerty_menubar/assets/keyboard.png`) ist **davon ausgenommen**; seine Weiterverbreitungsrechte sind nicht geklärt. Die öffentliche Sichtbarkeit des Repositories ist keine Erteilung von Bildrechten. Logitech-Bezeichnungen bleiben Eigentum ihrer Rechteinhaber; das Projekt ist nicht mit Logitech verbunden.
