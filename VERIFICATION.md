# Prüfung von v0.1.0

Lokal geprüft am 4. Oktober 2026 auf Apple Silicon, macOS 27.0.1, Python 3.14.7 und PyObjC 12.2.2. Der erste Download-Build benötigt **macOS 26 oder neuer und arm64**. Die native Oberfläche selbst verwendet APIs ab macOS 12; ein anderer Python-Build kann ältere Systeme unterstützen, wurde hier aber nicht geprüft.

## Nachgewiesen

| Prüfung | Tatsächliches Ergebnis |
|---|---|
| pytest | 23 Tests bestanden: Größen/Proportionen, Ressourcenpfade, Bildtransparenz, erhaltene weiße Beschriftung, CPU-Zeit-Auswertung |
| Ruff / Formatierung | Keine Befunde |
| Shell-Syntax | Beide Skripte mit `bash -n` geprüft |
| Python-Installation | `pip install -e .` und normaler Wheel-Build erfolgreich |
| Eigenständige `.app` | py2app-Build und strenge, tiefe Ad-hoc-Signaturprüfung erfolgreich |
| Installation | Kopie nach `~/Applications`, Start über LaunchServices erfolgreich |
| Ohne Entwicklungsdateien | `.venv` und Quellpaket vorübergehend umbenannt; installierte App startet und zeigt das Bild trotzdem |
| Fremde Laufzeitpfade | `lsof` zeigte keine geladenen Dateien aus dem Repository oder Homebrew in der installierten App |
| Instanzschutz | Zweiter direkter Start beendet sich; genau eine App-Instanz bleibt |
| Reale Bedienung | Physischer Linksklick öffnet; zweiter Klick und Escape schließen; Rechtsklick zeigt Beenden; Beenden beendet den Prozess; Neustart gelingt |
| Visuelle Prüfung | Transparenter Hintergrund und komplette, unverzerrte QWERTY-Tastatur im nativen Popover |
| Bild-Cache | Native Prüfung bestätigt die Wiederverwendung desselben NSImage-Objekts |
| 150 native Popover-Zyklen | RSS 81,66 → 81,97 MiB, Zuwachs 0,31 MiB; anschließende Leerlauf-CPU 0,102 % |
| Installierte App, 30 s Leerlauf | Je Messlauf etwa 90–103 MiB RSS, etwa 0,03–0,40 % eines CPU-Kerns |
| macOS-Speicher-Footprint | Etwa 42,4–42,5 MiB; gemessener Spitzenwert 43,0 MiB |
| Netzwerk | Keine App-Netzwerklogik; bei der Stichprobe keine offenen IP-Sockets |

Die sichtbaren abschließenden Prüfungen liefen auf dem in den Systemeinstellungen **oben rechts** angeordneten **24-FHD-144-V2 (2)**. Seine Display-ID war hier `2`; die von Cocoa vergebenen Namen für gleichartige Displays stimmen nicht zuverlässig mit den Nummern in den Systemeinstellungen überein. Monitoranordnung und Systemlayout wurden nicht verändert.

**RSS ist nicht gleich zusätzlicher RAM-Bedarf:** RSS enthält unter anderem gemeinsam genutzte Framework-Seiten. Der von macOS gemeldete physische Speicher-Footprint ist hier deutlich kleiner. Python/PyObjC bleiben größer als eine entsprechende reine Swift-App; ein Null-MB-Hintergrundprozess ist kein realistisches Ziel.

## Wiederholen

```bash
.venv/bin/pytest -q
.venv/bin/ruff check .
.venv/bin/ruff format --check .
bash -n scripts/build.sh scripts/install.sh
./scripts/build.sh
codesign --verify --deep --strict 'dist/QWERTY Menu Bar.app'
```

Native Bild-/Lebenszyklusprüfung mit ausdrücklich gewähltem Display:

```bash
.venv/bin/python -c 'from AppKit import NSScreen; print([(s.deviceDescription()["NSScreenNumber"], str(s.frame())) for s in NSScreen.screens()])'
.venv/bin/python -m tools.check_macos --display-id 2 --cycles 150 --idle-seconds 10
```

Diese Prüfung zeigt kurz ein echtes Popover am gewählten Bildschirm. Für die Wiederholungsprüfung deaktiviert sie Animationen und die Fokus-Rückgabe; sie ersetzt deshalb nicht den separaten tatsächlichen Menüleisten-Klick-/Escape-Test der verpackten App.

Die bereits gestartete, geschlossene App im Leerlauf messen:

```bash
pgrep -fl 'QWERTY Menu Bar'
.venv/bin/python -m tools.measure_process APP_PID --seconds 30
vmmap -summary APP_PID
```

Die Skripte verwenden bewusst grobe Regression-Budgets von 160 MiB RSS, weniger als 12 MiB Zuwachs bei wiederholtem Öffnen und weniger als 1 % Leerlauf-CPU. Das sind Warnschwellen, keine versprochenen Ressourcenwerte für jeden Mac.

## Grenzen

- Kein stunden-/tagelanger Dauertest und kein mathematischer Nachweis von Leak-Freiheit.
- Kein Intel-, älterer-macOS-, vollständiger VoiceOver- oder physischer Hellmodus-Test.
- Größenberechnung für mehrere Bildschirmbreiten automatisiert geprüft; kein vollständiger Hardware-/DPI-/Docking-Wechsel-Test.
- Standardverhalten „Klick außerhalb schließt“ wird von `NSPopoverBehaviorTransient` bereitgestellt, wurde nicht gesondert als realer Klickablauf dokumentiert.
- Lokaler, ad-hoc signierter Build geprüft. Apple Developer ID, Notarisierung und der komplette Gatekeeper-Ablauf auf einem anderen, frisch eingerichteten Mac sind nicht geprüft.
- Die optionale GitHub-Actions-Prüfung ist ausschließlich manuell auslösbar und wurde nicht gestartet, um keine potenziell kostenpflichtigen Runner-Minuten zu verbrauchen.
- Bildrechte für eine öffentliche Veröffentlichung sind ungeklärt; privates Repository und private Releases.
