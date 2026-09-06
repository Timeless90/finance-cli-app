# Modul 00 – Foundation, Data Governance & Betrieb

## Value Proposition

Dieses Modul macht alle anderen Module vertrauenswürdig und für eine Person
betreibbar: Daten werden einmal importiert, geprüft, unveränderlich gespeichert
und mit einer klaren Freigabe in fachliche Read-Models überführt. Es ersetzt
keine ERP- oder BI-Lösung, sondern bildet die kontrollierte Finanzdaten-Schicht
zwischen Quelle und CFO-Steuerung.

## Zielprozess

```text
Datei / ERP-Export → Mapping → Validierung & Abstimmung → Snapshot
→ Review → Freigabe → Publish → versionierte Read-Models
```

Jeder Schritt hat einen Status, eine Begründung, einen Actor und einen
Zeitstempel. Der Betreiber kann den gesamten Prozess lokal in der Data-&-
Governance-Oberfläche ausführen; es gibt keine versteckte Datenmanipulation.

## Fachlicher Umfang

| Fähigkeit | Produktverhalten |
| --- | --- |
| Import | CSV/Excel mit Quellmetadaten und gespeicherter Originaldatei importieren. |
| Mapping | Quellspalten kontrolliert auf Company, Konto, Periode, Betrag, Währung und Dimensionen abbilden. |
| Qualität | Pflichtfelder, Datentypen, Perioden, Währungen, Dubletten und Wertebereiche prüfen. |
| Abstimmung | Trial Balance und erwartete Referenzsumme prüfen; Blocker verhindern Publish. |
| Snapshot | Kanonische Daten per Hash versionieren und unveränderlich referenzieren. |
| Governance | Review, Approval, Audit und Trennung von Erfassung/Freigabe durchsetzen. |
| Read-Models | Nur aus veröffentlichten Snapshots fachliche Workspace-Projektionen erzeugen. |

## Bestehende Basis

Die lokale Anwendung unterstützt bereits Upload, Spaltenmapping, Validierung,
Abstimmung, Snapshot, Review, Approval und Publish in PostgreSQL; die
Originaldatei liegt im lokalen Import-Storage. Der lokale Gateway-Mechanismus
stellt Entwickler-, Controller- und CFO-Profile bereit. Die Publikation erzeugt
erste Live-Read-Models für Command Center, Planning, Performance, Profitability,
Liquidity und Data Governance.

## Umsetzungsreihenfolge

### DG-01 – Betriebsfester Kern

- Import-Queue mit Status, verständlichen Fehlern und Wiederholbarkeit.
- Persistente Snapshots, Import-Metadaten und Audit-Events.
- Sicheres lokales Backup von PostgreSQL und Import-Storage.
- Abnahme: Ein Neustart verliert weder Quelle, Snapshot noch publizierten
  Workspace.

### DG-02 – Semantisches Finanzmodell

- Versionierter Kontenplan und Mapping auf P&L-, Bilanz- und Cashflow-Positionen.
- Dimensionen für Cost Center, Profit Center, Produkt, Kunde und Segment.
- Mapping-Tests pro Quelle und Mapping-Vorschläge als Entwurf.
- Abnahme: Ein nicht vollständig zugeordnetes Konto wird sichtbar und blockiert
  die Module, die diese Position benötigen.

### DG-03 – Produktweite Governance

- Persistenter Run Store für Forecast-, Risk-, Action-, Capital- und Report-Runs.
- Ein Lifecycle-Modell: `DRAFT → IN_REVIEW → APPROVED → PUBLISHED/RETIRED`.
- Modellregister mit Version, Owner, Grenzen und Validierungsevidenz.
- Abnahme: Jede veröffentlichte Zahl verweist auf Snapshot, Run, Annahmen,
  Modell und Freigabe.

## Ein-Personen-Betrieb

- Es gibt genau einen täglichen Kontrollpunkt: die Data-&-Governance-Queue.
- Die lokale Rollenumschaltung testet Aufgabentrennung; produktiv ersetzt sie
  OIDC-Rollen, nicht zusätzliche manuelle Benutzerverwaltung.
- Nur zwei Backups sind erforderlich: PostgreSQL-Dump und Import-Storage. Beide
  werden mit Datum und Hash in einem dokumentierten Backup-Verzeichnis abgelegt.
- Monitoring bleibt zunächst einfach: strukturierte Application-Logs, Health
  Endpoint, Container-Restart und ein täglicher Backup-Check. Azure Monitor und
  Queue-Worker sind spätere Produktionsausbaustufen.

## Abhängigkeiten

Dieses Modul ist Voraussetzung für jedes schreibende oder berechnende Modul.
Command Center kann mit publizierten Basisprojektionen starten; Planning,
Profitability, Liquidity, Risk, Reporting und Copilot benötigen zusätzlich
Snapshot- und Governance-Lineage.

## Definition of Done

Ein Betreiber kann einen nicht-personenbezogenen ERP-Export hochladen, Fehler
korrigieren, die Abstimmung belegen, ihn mit getrennten lokalen Profilen
freigeben und anschließend in jedem berechtigten Workspace als Live-Daten sehen.
