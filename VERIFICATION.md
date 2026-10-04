# Prüfungen

## v1.0.0 — Standard-Hotkey, Design und Installation

Auf demselben Apple-Silicon-Mac wie v0.2.0 geprüft:

- **77 pytest-Tests bestanden**. Neue Prüfungen: `cmd+ctrl+shift+p` bei fehlenden Einstellungen; bestehende eigene und ausdrücklich deaktivierte Hotkeys bleiben erhalten; geglättete Bildkante erhält weiße Beschriftungen im Inneren.
- Ruff, Formatierung, Shell-Syntax und `git diff --check` ohne Befunde. Lokale Dokumentationslinks geprüft.
- Standardkürzel `⌃⇧⌘P` mit echter nativer Konfliktprüfung registriert und wieder freigegeben. Keine Benutzer-Einstellungen geändert. Das ist ein API-Nachweis, kein realer globaler Tastendruck.
- Native Recorder-Selektoren erneut mit isolierten Testeinstellungen geprüft: gültiges Kürzel speichern, Systemkonflikt ablehnen, alte Belegung behalten, Kürzel entfernen. Native Papierkorb-API erneut nur mit temporärer App-Kopie geprüft.
- Native Prüfwerkzeuge starten jetzt mit eigenen, ausdrücklich deaktivierten Test-Hotkeys und laden keine Benutzer-Belegung beim Bootstrap.
- Tastaturkante auf dunklem Hintergrund vorher/nachher visuell verglichen: helle JPEG-Randpixel entfernt. Native AppKit-Vorschau der Kopfzeile und des Zahnrads normal/gedrückt geprüft: 36-Punkt-Klickfläche, 22-Punkt-Symbol, neutral graue statt grüne Rückmeldung. Diese Ansicht wurde über natives View-Caching gerendert, nicht als vollständiger Desktop-Klickablauf geprüft.
- Standalone-Build mit Bundle-Version **1.0.0**, Mindestversion **macOS 26**, erfolgreicher strenger Ad-hoc-Signaturprüfung und gültiger ZIP-Prüfsumme. Nach lokaler Installation über LaunchServices gestartet; Prozess läuft.

**Weiterhin offen:** Vollständige sichtbare Menü-/Recorder-/Hotkey-Benutzerabläufe, echte Login-Item-Freigabe mit Ab-/Anmeldung, Deinstallations-Bestätigungsdialog und Gatekeeper auf einem frisch eingerichteten anderen Mac. Keine neue Langzeit-/Intel-/ältere-macOS-Prüfung. Nicht mit Apple Developer ID signiert oder notarisiert; Bildrechte weiterhin ungeklärt. v1.0.0 bedeutet keine vollständige Konflikt- oder Kompatibilitätsgarantie.

## v0.2.0 — Einstellungen und globale Hotkeys

Geprüft am 4. Oktober 2026 auf demselben Apple-Silicon-Mac (macOS 27.0.1, Python 3.14.7, PyObjC 12.2.2). Die native Login-Item-API setzt macOS 13 voraus; der konkrete Download-Build weiterhin macOS 26+.

- **74 pytest-Tests bestanden**, einschließlich Validierung/Kombinationen, aktivierten Systemkonflikten, konservativen App-Regeln, atomarem JSON-Speichern, Rücknahme fehlgeschlagener Registrierungen, Wiederholungsfilter, Login-Item-Status und sicherer Bundle-/Dateiprüfung.
- Ruff und Formatierung geprüft.
- Native `CopySymbolicHotKeys`-Abfrage: 234 Definitionen, davon 176 aktiviert. `⌘Leertaste` als echter macOS-Konflikt abgelehnt.
- Echter Konflikt mit einem **zweiten Prozess und exklusiver Registrierung** erkannt. Gegenprobe mit nicht-exklusiver Registrierung zeigt die OS-Grenze: diese Konflikte werden nicht verlässlich gemeldet. Finale Registrierung bewusst geteilt, damit sie andere geteilte Registrierungen nicht verdrängt.
- Native Recorder-Steuerung mit temporären Einstellungen: gültige Kombination gespeichert, macOS-Konflikt abgelehnt, alter Hotkey erhalten, Entfernen erfolgreich. Dabei native Controls/Selektoren aufgerufen, kein tatsächlicher physischer Tastendruck.
- Native Papierkorb-API mit einer eigenen temporären `.app`-Kopie geprüft: nur Testkopie verschoben, Original erhalten und Testkopie danach aufgeräumt. Die Benutzer-App wurde nicht deinstalliert.
- 100 native Popover-Lebenszyklen: RSS etwa 86,16 → 86,31 MiB, Zuwachs rund 0,16 MiB, anschließende Leerlauf-CPU etwa 0,103 %.
- Kein Autostart aktiviert und kein globales Testkürzel dauerhaft hinterlassen. Autostart-API-Aufrufe/statusabhängige UI mit Test-Service geprüft; echte Registrierung plus Ab-/Anmeldung noch nicht nachgewiesen.

**Noch offen:** Der Desktop wurde während der Arbeit gesperrt. Sichtbarer Zahnrad-/Menü-/Recorder-Ablauf, echte globale Tastendrücke, Login-Item-Freigabe/Anmeldung und der reale Deinstallations-Bestätigungsdialog sind daher nicht abschließend als Benutzerablauf geprüft. Kein Versprechen vollständiger Hotkey-Konfliktfreiheit oder vollständiger UI-/Langzeit-/Kompatibilitätsabdeckung.

Reproduzierbare native Prüfungen, ohne die Benutzer-App zu deinstallieren oder Autostart einzurichten:

```bash
.venv/bin/python -m tools.check_hotkeys_macos
.venv/bin/python -m tools.check_settings_macos
.venv/bin/python -m tools.check_macos --display-id DISPLAY_ID --cycles 100 --idle-seconds 10
```

Für sichtbare Tests erst entsperren und die aktuelle Monitoranordnung prüfen; Display-IDs/Koordinaten können sich beim Schließen des Laptop-Displays ändern. Felix möchte den rechten Monitor **24-FHD-144-V2 (2)** verwenden.

## Historischer Nachweis: v0.1.0

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
- Bildrechte für eine öffentliche Weiterverbreitung sind weiterhin ungeklärt. Beim v0.1.0-Nachweis waren Repository und Releases privat; seit v0.2.0 ist das Repository auf ausdrücklichen Wunsch öffentlich. Die MIT-Lizenz schließt das Foto weiterhin aus.
