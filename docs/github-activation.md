# GitHub-Aktivierung

Stand 2026-09-06: Das Repository `Timeless90/finance-cli-app` ist als Remote verbunden. Das private [Finance CLI App Project #2](https://github.com/users/Timeless90/projects/2) ist eingerichtet und mit dem Repository verknüpft; siehe [Arbeitsablauf](development/github-project-workflow.md). Die lokalen Strukturänderungen sind weiterhin unveröffentlicht.

Die Workflows `Quality` und `Security` und die Dependabot-Konfiguration sind lokal vorbereitet. Diese Project-Einrichtung hat keine Branch-Regeln, Security-Schalter oder Deployment-Einstellungen aktiviert; deren tatsächlicher Stand ist im Betriebs-Epic zu prüfen.

Nach dem freigegebenen Anlegen/Veröffentlichen des konkreten Repositorys:

1. Lockfiles, OpenAPI und den generierten Client aus dem erfolgreichen Bootstrap mit versionieren.
2. Actions aktivieren und die tatsächlichen Checks als Required Checks in einem passenden Ruleset auswählen. Menschliche Review-Gates, Squash Merge und Branch-Regeln an das Projekt anpassen.
3. Dependabot Alerts, Security Updates, GitHub Secret Scanning und Push Protection in den Repository-Einstellungen aktivieren, soweit Konto/Plan sie unterstützen. Eine lokale YAML-Datei kann diese serverseitigen Schalter nicht ersetzen.
4. Verfügbarkeit von CodeQL und Dependency Review für das konkrete öffentliche/private Repository prüfen. Die vorbereiteten Jobs führen echte Prüfungen durch und können bei fehlenden GitHub-Berechtigungen oder Features fehlschlagen; sie werden nicht als automatisch eingerichtet behauptet.
5. Findings prüfen und Änderungen getrennt freigeben. Ein fehlgeschlagener Image- oder Dependency-Scan wird nicht automatisch ignoriert oder durch ungeprüfte Updates repariert.

`Security` enthält CodeQL, Dependency Review, Secret-Scanning des ausgecheckten Quellcodes sowie Trivy-Scans der gebauten Backend-/Frontend-Images. GitHub Secret Scanning ergänzt die Prüfung der Repository-Historie. Vorhandene lokale Hooks bleiben unberührt.

Release Please, Release-/Deployment-Zugänge sowie dev/test/prod werden mit dem tatsächlichen Zielprojekt eingerichtet; hier werden keine produktiven Umgebungen oder Tokens angenommen.

Quellen: [Dependabot-Ecosysteme](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories), [Trivy Action](https://github.com/aquasecurity/trivy-action).
