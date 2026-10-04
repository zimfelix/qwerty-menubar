# QWERTY Menu Bar

Eine QWERTY-Tastatur als schnelle Referenz in deiner **macOS-Menüleiste**. Öffnen per Tastatur-Icon oder **Command + Control + Shift + P** (`⌘⌃⇧P`).

**[App herunterladen](https://github.com/zimfelix/qwerty-menubar/releases/latest/download/QWERTY-Menu-Bar-macOS-arm64.zip)** · [Alle Releases](https://github.com/zimfelix/qwerty-menubar/releases) · [Prüfnachweise](VERIFICATION.md)

**Voraussetzungen:** Apple Silicon (M1 oder neuer) und **macOS 26 oder neuer**. Python ist enthalten — kein Terminal, Git oder zusätzliches Python nötig. Für Intel-Macs und ältere macOS-Versionen gibt es derzeit keinen geprüften Download.

## Installieren — in vier Schritten

1. Oben auf **App herunterladen** klicken.
2. Die ZIP im Finder öffnen. Darin liegt **QWERTY Menu Bar.app**.
3. Die `.app` in den Ordner **Programme** ziehen. Nicht dauerhaft aus der ZIP oder dem Downloads-Ordner starten.
4. Die App in Programme doppelklicken. Rechts in der Menüleiste erscheint ein kleines Tastatur-Icon. Jetzt **⌘⌃⇧P** drücken oder das Icon anklicken.

Es erscheint **kein Dock-Icon**. Das ist bei dieser Menüleisten-App beabsichtigt. Autostart ist zunächst **aus**.

### Falls macOS das Öffnen blockiert

Die App ist **ad-hoc signiert, aber noch nicht mit Apple Developer ID signiert oder notarisiert**. Bei einem heruntergeladenen Build kann Gatekeeper deshalb eine Sicherheitsbestätigung verlangen:

1. Die App einmal zu öffnen versuchen.
2. **Systemeinstellungen → Datenschutz & Sicherheit** öffnen.
3. Bei der Meldung zur App **Dennoch öffnen** wählen, sofern macOS diese Option anbietet, und bestätigen.

Nur für ein selbst gebautes oder vertrauenswürdiges Release bestätigen. Gatekeeper nicht global deaktivieren. Die App fordert keine Bedienungshilfen- oder Input-Monitoring-Berechtigung an.

## Benutzen

| Aktion | So geht’s |
|---|---|
| Tastatur anzeigen / ausblenden | **⌘⌃⇧P** oder Linksklick auf das Tastatur-Icon |
| Einstellungen öffnen | Zahnrad oben rechts im Tastaturfenster; alternativ Rechtsklick auf das Menüleisten-Icon |
| Automatisch beim Login starten | **Autostart · Aus** anklicken; bei angezeigter Freigabe **In macOS freigeben …** wählen |
| Eigenes Tastenkürzel setzen | **Tastenkürzel …** → Aufnahme anklicken und Kombination drücken, oder manuell eingeben und **Prüfen** wählen |
| App schließen | **Beenden** — ein aktivierter Autostart bleibt für die nächste Anmeldung erhalten |
| App entfernen | **Deinstallieren …** und ausdrücklich bestätigen |

Das Tastaturfenster schließt auch mit Escape oder durch einen Klick außerhalb. Die App ist eine **Layout-Referenz**, kein Remapping-Werkzeug: Sie ändert keine Tastaturbelegung und keine macOS-Systemkürzel.

## Standard-Hotkey und Konflikte

Bei einer neuen Installation ist **Command + Control + Shift + P** voreingestellt. Bestehende eigene Hotkeys und bewusst entfernte Hotkeys bleiben bei Updates erhalten. Zum Standard zurückwechseln: Im Tastenkürzel-Fenster `cmd+ctrl+shift+p` eingeben und **Prüfen** wählen.

Vor der Aktivierung werden aktivierte macOS-Systemkürzel, typische App-/Textkürzel und erkennbare Konflikte mit exklusiven globalen Hotkeys geprüft. Bei einem erkannten Konflikt wird die Kombination nicht aktiviert; eine bestehende Belegung bleibt erhalten.

**Grenze:** Nicht-exklusive globale und app-interne Kürzel anderer Programme lassen sich nicht vollständig abfragen. Vollständige Konfliktfreiheit kann macOS nicht garantieren. Die endgültige Registrierung ist nicht exklusiv und verdrängt keine vorhandene geteilte Registrierung.

Wenn eine andere App oder macOS den Tastendruck bereits abfängt, nutze die manuelle Eingabe im Tastenkürzel-Fenster. Mindestens `⌘`, `⌃` oder `⌥` plus eine Taste; weitere Modifier wie `⇧` sind möglich. Fn oder reine Modifier allein sind nicht unterstützt. Manuelle Zeichennamen verwenden QWERTY-Tastenpositionen.

## Aktualisieren

1. Alte App über **Beenden** schließen.
2. Neue ZIP herunterladen und entpacken.
3. Die `.app` im Ordner Programme ersetzen und wieder starten.

Eigene Hotkey-Einstellungen bleiben erhalten. Wenn macOS die Freigabe des Anmeldeobjekts erneut verlangt, diese über das Einstellungsmenü prüfen. Bei einem fehlgeschlagenen Download erneut aus den offiziellen Releases herunterladen.

## Deinstallieren

Am einfachsten: **Zahnrad → Deinstallieren …**. Die laufende App wird nach Bestätigung in den Papierkorb verschoben. Eigener Autostart, Hotkey und Einstellungen werden entfernt; das Quellprojekt bleibt unberührt.

Alternativ Autostart ausschalten, **Beenden** wählen und die `.app` in den Papierkorb ziehen. Optional eigene Restdateien entfernen:

- `~/Library/Application Support/dev.zimfelix.qwerty-menubar/`
- `~/Library/Caches/dev.zimfelix.qwerty-menubar/`

## Für Entwickler

Die Oberfläche verwendet native AppKit-Elemente über PyObjC: kein Electron, kein Browser, keine Netzwerklogik und keine Polling-Timer. Das Tastaturbild wird einmal geladen und wiederverwendet.

Quellstart, Build und Prüfungen: **[DEVELOPMENT.md](DEVELOPMENT.md)**. Tatsächliche Prüfergebnisse und offene Nachweise: **[VERIFICATION.md](VERIFICATION.md)**.

## Lizenz

Der eigene Programmcode steht unter der **MIT-Lizenz**. Das bereitgestellte Logitech-Tastaturfoto ist davon ausgenommen; seine Weiterverbreitungsrechte sind ungeklärt. Ein öffentliches Repository erteilt keine Bildrechte. Dieses Projekt ist nicht mit Logitech verbunden.
