# Modul 07 – Reporting Studio

## Value Proposition

Reporting Studio erstellt Management- und externe Artefakte aus exakt den
gleichen freigegebenen Werten, die im Dashboard stehen. Es verringert den
monatlichen Kopieraufwand und verhindert, dass Zahlen, Texte und Freigaben
auseinanderlaufen.

## Zielworkflow

```text
approved Read-Models / Runs → versioniertes Template → Report Draft
→ Review → (bei extern: Human Approval) → Export → unveränderliches Artefakt
```

Das Reporting-Modul berechnet keine Kennzahlen. Jede Zahl und jede wesentliche
Aussage trägt Referenzen auf Snapshot und genehmigten Run.

## Fachlicher Umfang

- Versionierte Templates für Management Pack, Forecast Report, Board Risk Pack,
  Lagebericht-Entwurf und Audit Evidence Pack.
- Pflichtsektionen und referenzierte `ReportValue`-/Narrative-Bausteine.
- Deterministischer Content-Hash; Bericht-ID und Zeitstempel ändern den Inhalt
  nicht rückwirkend.
- JSON, CSV, XLSX, PDF und PPTX als Exporte; ESEF/XBRL bleibt später.
- Trennung von Draft, Review, Approval, Publication und Export.

## Bestehende Basis und Ziel-Lücken

Template-/Report-Erzeugung, Lineage-Prüfung, Approval und Exporte sind im
Backend vorhanden. Noch zu ergänzen sind PostgreSQL-Metadaten, lokaler
Artefakt-Store, asynchrone Export-Jobs für große Packs und die Live-Oberfläche
für Template-, Report- und Download-Lifecycle.

## Umsetzungsreihenfolge

### RE-01 – Management Pack aus freigegebenen Quellen

- Persistente Report-Drafts und lokale Artefaktablage.
- Frontend: Template wählen, Quellenstatus prüfen, Draft erzeugen, Inhalt und
  Lineage anzeigen.
- Abnahme: Ein Management Pack übernimmt einen genehmigten Wert unverändert;
  fehlende oder nicht freigegebene Quellen blockieren die Erzeugung.

### RE-02 – Review, Approval und Export

- Externe Templates verlangen getrennte menschliche Freigabe.
- Export-Jobs erhalten Status, Retry und Artefakt-Metadaten.
- Abnahme: Ein Lagebericht kann vor Approval nicht exportiert werden; das
  exportierte Artefakt verweist auf Template- und Inhaltsversion.

### RE-03 – Wiederkehrender Monatsreport

- Template-Schedule als expliziter, manuell auslösbarer Monatsprozess; keine
  unüberwachte automatische Publikation.
- Abnahme: Ein Betreiber kann einen fehlgeschlagenen Export ohne Zahlenverlust
  wiederholen und erkennt eindeutig den verwendeten Datenstand.

## Abhängigkeiten

Erfordert Modul 00 und konsumiert ausschließlich publizierte Ergebnisse aus
Planning, Performance, Liquidity, Risk und Actions/Capital. Der Copilot kann
Entwürfe liefern, aber nie Report Approval oder Veröffentlichung auslösen.

## Definition of Done

Ein Monats-Management-Pack lässt sich mit einem kontrollierten Durchlauf
erzeugen, prüfen, exportieren und später mit allen Zahlenquellen reproduzieren.
