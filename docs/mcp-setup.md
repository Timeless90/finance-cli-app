# MCP-Ergänzungen für das Development-Template

Alle acht Server sind für beide Clients konfiguriert:

- GitHub Copilot: `.vscode/mcp.json`, Zugangsdaten über geschützte VS-Code-Inputs.
- Codex: `.codex/config.toml`, Zugangsdaten über die unten genannten Umgebungsvariablen beziehungsweise OAuth.

Bei Änderungen Server-URLs, Paketversionen und Schutzschalter in beiden Dateien abgleichen.

| Server | Einrichtung beim ersten Start |
|---|---|
| GitHub | GitHub-Anmeldung in VS Code |
| Playwright | Bereits vorhandenes lokales Paket; keine Anmeldung |
| 21st | Aktuellen API-Key in der geschützten VS-Code-Abfrage eingeben |
| Microsoft Learn | Keine Anmeldung |
| Context7 | Browser-Anmeldung über OAuth |
| shadcn | Automatischer Download von shadcn 4.21.0 über pnpm beim ersten Start |
| Grafana | Download von mcp-grafana 1.3.0 über uv; Token eines Viewer-Service-Accounts eingeben |
| PostgreSQL / DBHub | Download von @bytebase/dbhub 1.2.3 über pnpm; URI eines DB-Benutzers mit Leserechten eingeben |

Die Pakete werden als separate Werkzeuge gestartet. Anwendungs-Abhängigkeiten und Lockfiles bleiben unverändert. Die direkten Werkzeugversionen sind festgelegt; pnpm dlx ist keine vollständige Sperre sämtlicher transitiver Abhängigkeiten.

## Aktivierung in GitHub Copilot

Nach der Übernahme in VS Code `MCP: List Servers` öffnen und die gewünschten Server starten. Server-Vertrauen und Account-Anmeldungen erfolgen in VS Code. Die Datei aktiviert keine pauschale Tool-Freigabe.

Für shadcn ist das Arbeitsverzeichnis ausdrücklich `frontend`, damit die vorhandene `components.json` gefunden wird. Komponentenänderungen erfolgen erst auf einen entsprechenden Auftrag.

Grafana benötigt den laufenden Observability-Stack (`mise exec -- make observability-up`). In Grafana unter Administration → Users and access → Service accounts einen Account mit Rolle **Viewer** anlegen und dessen Token ausschließlich in die VS-Code-Abfrage eingeben. Der MCP-Server startet zusätzlich mit `--disable-write` und ausschließlich den Kategorien search, datasource, dashboard, prometheus und loki.

PostgreSQL benötigt die laufende Entwicklungsdatenbank (`mise exec -- make infra-up`). Verwende einen eigenen Datenbankbenutzer mit CONNECT, USAGE auf die benötigten Schemas und SELECT auf die benötigten Tabellen. Der Benutzer darf weder Eigentümer noch Superuser sein und keine schreibenden Rollen erben. Die App-Zugangsdaten `template` sind dafür ungeeignet. Für künftige Tabellen müssen passende Standardrechte durch den jeweiligen Tabellenbesitzer eingerichtet werden.

Format der geschützten URI: `postgres://BENUTZER:URL_KODIERTES_PASSWORT@127.0.0.1:15432/template?sslmode=disable`. `sslmode=disable` gilt nur für die lokale Docker-Datenbank. Für entfernte Datenbanken die vorgesehenen TLS-Einstellungen verwenden.

DBHub erhält in beiden Clients den Lesemodus über `.vscode/mcp/dbhub.toml`, begrenzt SQL-Ergebnisse auf 100 Zeilen und stellt Schema-Suche und Ausführungspläne bereit. Seine Startumgebung liegt in `.vscode/mcp`, damit die automatische dotenv-Suche nicht im Anwendungs-Root beginnt. In diesem Verzeichnis keine `.env` ablegen. Copilot übergibt die URI über einen VS-Code-Input; Codex übernimmt die ausdrücklich bereitgestellte Umgebungsvariable.

Datenbank-Leserechte und Grafana-Token wurden nicht angelegt oder geprüft; sie müssen vor dem jeweiligen Serverstart bereitstehen. Die MCP-Schalter ersetzen keine serverseitigen Zugriffsrechte.

## Aktivierung in Codex

1. Das Repository als Projekt öffnen und ihm in Codex vertrauen. Projektkonfigurationen werden nur für vertrauenswürdige Projekte geladen.
2. `mise`, Git und eine POSIX-Shell müssen im PATH des Codex-Prozesses liegen. Abhängigkeiten mit `mise exec -- make install` bereitstellen. Codex im Repository starten; die STDIO-Befehle ermitteln den Git-Root und funktionieren auch aus Unterverzeichnissen sowie bei Pfaden mit Leerzeichen.
3. Benötigte Zugangsdaten über die Umgebung des startenden Codex-Prozesses bereitstellen:

   | Variable | Verwendung |
   |---|---|
   | `CODEX_GITHUB_TOKEN` | GitHub-Token mit Zugriff auf die benötigten Repositories und Aktionen |
   | `TWENTY_FIRST_API_KEY` | 21st-API-Key |
   | `GRAFANA_SERVICE_ACCOUNT_TOKEN` | Token des Grafana-Viewer-Service-Accounts |
   | `MCP_POSTGRES_DSN` | Verbindungs-URI des PostgreSQL-Benutzers mit Leserechten |

   Keine echten Werte in Konfigurationsdateien, Dokumentation oder Shell-History schreiben. Eine bereits laufende VS-Code-Instanz übernimmt spätere Terminal-Exporte nicht automatisch; die Codex-Erweiterung muss in einer Umgebung mit diesen Variablen gestartet werden. Copilot-Inputs werden nicht an Codex weitergegeben.
4. Für Context7 im Repository `codex mcp login context7` ausführen und die Browser-Anmeldung abschließen. GitHub verwendet hier den oben genannten Bearer-Token unabhängig von der Copilot-Anmeldung.
5. Codex beziehungsweise die Erweiterung neu starten. Mit `codex mcp list` die Konfiguration und in einer neuen Codex-Sitzung mit `/mcp` die Verbindungen prüfen. Ein Listeneintrag allein ist kein erfolgreicher Verbindungstest.

Microsoft Learn, Playwright und shadcn benötigen keine Zugangsdaten. Grafana und PostgreSQL benötigen zusätzlich die oben beschriebenen laufenden Dienste. Fehlende Zugangsdaten müssen vor Nutzung des jeweiligen Servers bereitstehen. Nicht benötigte Server können in Codex mit `enabled = false` in ihrer Server-Tabelle deaktiviert werden.

Beide Clients können dieselben Dienste verwenden. Sie starten eigene STDIO-Prozesse; Codex schreibt Playwright-Artefakte separat nach `.local/playwright-mcp-codex/`. Es werden keine globalen Codex-Einstellungen oder pauschalen Tool-Freigaben gesetzt.

Siehe die [offizielle Codex-MCP-Dokumentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) für Projektkonfiguration, Umgebungsvariablen und OAuth.

## Bisheriger Prüfstand und Grenzen

- Codex-Ergänzung: JSON/TOML und Übereinstimmung aller acht Servernamen und HTTP-URLs geprüft. Die installierte Codex-CLI 0.153.0 akzeptiert die Konfiguration in einer isolierten Testumgebung ohne Zugangsdaten.
- Die vier Codex-STDIO-Startbefehle wurden mit einem Ersatzprogramm für mise auf Shell-Syntax, Arbeitsverzeichnisse und Argumente geprüft, auch beim Aufruf aus einem Unterverzeichnis. Dabei wurden keine Server gestartet.
- Grafana-Leseschalter und DBHub-Lesekonfiguration wurden lokal geprüft. Ein unabhängiges Security-Review-Werkzeug war nicht verfügbar; eine externe Sicherheitsfreigabe oder vollständige Live-Abnahme ist damit nicht erfolgt.

Prüfnotizen aus der bisherigen Copilot-Einrichtung:

- JSON und TOML geparst; alle Input-Verweise geprüft.
- Bestehende vier Server und Inputs werden beim Zusammenführen erhalten; abweichende gleichnamige Einträge führen zum Abbruch vor Änderungen.
- Byte-identische Sicherung der zu ersetzenden Dateien; Wiederholung ohne Änderung möglich.
- Die Startbefehle wurden anhand der offiziellen Dokumentation und Veröffentlichungen geprüft.
- Playwright wurde zuvor über initialize und tools/list mit 21 Tools geprüft.
- Die vier neuen Server wurden in dieser Sitzung nicht live gestartet: Paketdownloads sind gesperrt; Grafana- und PostgreSQL-Lesezugänge liegen nicht vor. Keine vollständige MCP-Live-Abnahme behauptet.
- `.env`, Secrets, bestehende Hooks, Security-Regeln und VS-Code-Keybindings bleiben unangetastet.

## Quellen

- Context7 OAuth: https://context7.com/docs/resources/all-clients
- shadcn MCP: https://ui.shadcn.com/docs/mcp
- shadcn 4.21.0: https://github.com/shadcn-ui/ui/releases/tag/shadcn@4.21.0
- Grafana 1.3.0: https://github.com/grafana/mcp-grafana/releases/tag/v1.3.0
- Grafana-Konfiguration: https://github.com/grafana/mcp-grafana/blob/v1.3.0/README.md
- DBHub 1.2.3: https://github.com/bytebase/dbhub/releases/tag/v1.2.3
- DBHub TOML: https://dbhub.ai/config/toml
- DBHub CLI: https://dbhub.ai/config/command-line
