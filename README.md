# QWERTY Menu Bar

Eine kleine **Python-App für die macOS-Menüleiste**: Tastatur-Icon anklicken, QWERTY-Layout einer Logitech-Mini-Tastatur nachsehen, weiterarbeiten.

- Native AppKit-Oberfläche, kein Electron und kein Browser.
- Nur das Tastaturbild im Popover, proportional skaliert und mit transparentem Hintergrund.
- Linksklick öffnet/schließt; Klick außerhalb oder Escape schließt. Rechtsklick → **Beenden**.
- Passt sich dem Bildschirm an; das Menüleisten-Icon unterstützt Hell-/Dunkelmodus.
- Kein Dock-Icon, kein Tastaturmitschnitt, keine Bedienungshilfen-/Input-Monitoring-Berechtigung.
- Keine Netzwerkzugriffe, Timer, Hintergrundjobs oder automatischen Login-Einträge.
- Eine Instanz, ein bei Bedarf geladenes und anschließend wiederverwendetes Bild.

Das ist eine **Layout-Referenz**, kein Remapping-Werkzeug. Die aufgedruckten Mac-/Windows-/Fn-Belegungen sind sichtbar; tatsächliche Shortcuts hängen von macOS, App und Tastaturkonfiguration ab. Die App ändert weder das Systemlayout noch Tastenkombinationen.

## Installation ohne Python

1. In den [Releases](https://github.com/zimfelix/qwerty-menubar/releases) die passende macOS-ZIP herunterladen. Private Releases benötigen einen angemeldeten GitHub-Account mit Repository-Zugriff.
2. ZIP entpacken und **QWERTY Menu Bar.app** nach `~/Applications` oder `/Applications` ziehen.
3. App öffnen. Das kleine Tastatur-Icon erscheint rechts in der Menüleiste.

Die erste Veröffentlichung benötigt **Apple Silicon (arm64) und macOS 26 oder neuer**. Intel-Macs und ältere macOS-Versionen benötigen einen passenden eigenen Python-/App-Build. Ein Internetzugang oder installiertes Python ist nach dem Download nicht nötig.

Alternativ mit bereits angemeldeter GitHub CLI:

```bash
gh release download v0.1.0 --repo zimfelix/qwerty-menubar --pattern '*.zip' --dir ~/Downloads
```

Danach die ZIP entpacken und die `.app` wie oben installieren.

### Gatekeeper

Der Build ist **ad-hoc signiert, nicht mit einer Apple Developer ID signiert oder notarisiert**. Bei heruntergeladenen Builds kann macOS eine Sicherheitsbestätigung verlangen: Öffnungsversuch, anschließend **Systemeinstellungen → Datenschutz & Sicherheit → Dennoch öffnen**, sofern angeboten. Nur für ein selbst gebautes oder vertrauenswürdiges Release bestätigen. Keine globale Gatekeeper-Abschaltung und kein automatisches Entfernen von Quarantäne-Attributen.

## Aus dem Quellcode starten

Benötigt macOS und Python 3.12 oder neuer:

```bash
git clone git@github.com:zimfelix/qwerty-menubar.git
cd qwerty-menubar
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m qwerty_menubar
```

Im Laufzeitpfad wird nur PyObjC/Cocoa zusätzlich zu Python benötigt. Pillow und py2app sind reine Entwicklungs-/Build-Abhängigkeiten.

## Selbstständige .app bauen und lokal installieren

```bash
./scripts/build.sh
./scripts/install.sh
```

Der Build enthält Python und die benötigten Bibliotheken; die installierte `.app` benötigt weder Repository noch `.venv`. Ergebnis: `dist/QWERTY Menu Bar.app` plus ZIP und SHA-256-Datei. Installation erfolgt ohne Administratorrechte nach `~/Applications`; kein Login-Item wird eingerichtet. Vor Updates die laufende App beenden und die alte Kopie verschieben.

## Entwicklung und Prüfungen

```bash
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

**Aktueller Nachweis:** 23 Logik-/Asset-Tests bestanden; 150 native Öffnen-/Schließen-Zyklen mit etwa 0,31 MiB RSS-Zuwachs; installierte App mit etwa 42–43 MiB physischem Speicher-Footprint. Messverfahren, tatsächliche UI-Prüfungen und Grenzen stehen in [VERIFICATION.md](VERIFICATION.md).

Native UI- und Ressourcenprüfungen benötigen einen angemeldeten macOS-Desktop und einen bewusst gewählten Testmonitor. Grüne Logiktests sind kein Nachweis für Gatekeeper, alle Displays oder langfristigen Speicherverbrauch. Die optionale GitHub-Actions-Prüfung läuft nur auf manuellen Aufruf; bei privaten Repositories können macOS-Runner-Minuten kostenpflichtig sein.

Die Bildvorbereitung ist reproduzierbar, wenn das bereitgestellte Original vorhanden ist:

```bash
.venv/bin/python tools/prepare_image.py /path/to/original.jpg
```

Nur randverbundene, nahezu weiße Pixel werden entfernt — nicht weiße Beschriftungen innerhalb der Tastatur.

## Aufbau

```text
Menüleisten-Klick → AppKit-Popover → transparentes PNG
                               ↳ einmal laden, danach wiederverwenden

Python + PyObjC → py2app → eigenständig startbare .app
```

- `qwerty_menubar/app.py`: native Oberfläche und Instanzschutz
- `qwerty_menubar/layout.py`: Größenberechnung und Asset-Suche
- `tools/prepare_image.py`: Freistellung und Icons, nur bei der Entwicklung
- `scripts/`: Build und Installation
- `tests/`: nachvollziehbare automatische Prüfungen

## Deinstallation

Rechtsklick auf das Icon → **Beenden**, anschließend die `.app` löschen. Optional den leeren Instanz-Lock unter `~/Library/Caches/dev.zimfelix.qwerty-menubar` entfernen. Keine Dienste oder Login-Einträge müssen entfernt werden.

## Lizenz und Bildrechte

Der selbst erstellte Programmcode steht unter der MIT-Lizenz. Das bereitgestellte Logitech-Tastaturfoto (`qwerty_menubar/assets/keyboard.png`) ist **davon ausgenommen**; seine Veröffentlichungs-/Weiterverbreitungsrechte sind nicht geklärt. Logitech-Bezeichnungen bleiben Eigentum ihrer jeweiligen Rechteinhaber. Dieses Projekt ist nicht mit Logitech verbunden. Repository und Release bleiben deshalb zunächst privat.
