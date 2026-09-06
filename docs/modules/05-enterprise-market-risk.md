# Modul 05 – Enterprise & Market/Treasury Risk

## Value Proposition

Das Modul verbindet ein verantwortetes Risikoregister mit quantifizierter
Verlustverteilung und Marktpreisexposures. Es macht deutlich, welches Risiko
real ist, wie es aggregiert wird und welche Annahmen hinter einer Kennzahl
stehen – statt Risiken in isolierten Heatmaps und Simulationen zu halten.

## Zwei bewusst getrennte Teilbereiche

| Teilbereich | Startnutzen | Voraussetzung |
| --- | --- | --- |
| Enterprise Risk | Risiken, Controls, Appetite und Plan-Auswirkung | Modul 00, Planning für Risk-to-Plan |
| Market/Treasury Risk | FX-/Zins-/Commodity-Exposure, VaR/ES, Hedges | zusätzliche Marktzeitreihen und Treasury-Daten |

Market Risk ist für einen Einzelbetreiber ausdrücklich später und optional.
Enterprise Risk liefert bereits den wichtigen Governance- und Entscheidungsnutzen.

## Enterprise-Risk-Workflow

```text
Risk Owner: Register + Control → Quantifizierung → Aggregations-Run
→ Appetite-/Limit-Prüfung → Review/Freigabe → Risk-to-Plan oder Action → Report
```

- Register: Ursache, Ereignis, Owner, Kategorie, Zeitraum, Brutto-/Netto-Risiko,
  Controls und Double-Count-Gruppe.
- Quantifizierung: Wahrscheinlichkeit/Frequenz sowie empirische, lognormale,
  Pareto- oder diskrete Schadenverteilung.
- Aggregation: reproduzierbare Monte-Carlo-Simulation, validierte
  Korrelationsmatrix, P50/P90/P95/P99 und Expected Shortfall.
- Appetite: Limit, Warnschwelle, Headroom und Eskalation nach Kategorie, KPI
  oder Risikotragfähigkeit.
- Plan-Integration: explizite GuV-/Bilanz-/Cashflow-Auswirkung mit
  `impact_key`; Doppelzählungen sind verboten.

## Market-/Treasury-Risiko – späterer Ausbau

- Exposure Aggregation, Sensitivität, Historical/Student-t VaR und Expected
  Shortfall sind der Einstieg.
- GARCH, HMM, EVT und Copula sind nur aktiv, wenn definierte
  Stabilitäts-/Backtest-Gates einen Mehrwert gegen einfache Baselines belegen.
- Hedge-Effektivität sowie Kupiec-/Christoffersen-Backtests sind Bestandteil
  eines genehmigten Modellruns, keine Dashboard-Dekoration.

## Bestehende Basis und Ziel-Lücken

Enterprise-Risk- und Market-Risk-Berechnungskerne sowie API-Contracts bestehen.
Sie verwenden noch in-memory-orientierte Workflows. Notwendig sind daher zuerst
persistente Register, Controls, Runs, Modellregister-Verknüpfung,
Review/Publish und Live-Read-Models.

## Umsetzungsreihenfolge

### RI-01 – Risk Register und Appetite

- Persistiertes Register, Controls, Owner, Limits und Audit.
- Frontend: Liste, Heatmap, Limitstatus und klare Empty-States.
- Abnahme: Ein Risiko ist auf Owner, Control und Scope zurückführbar; kein
  fremder Company-Scope wird angezeigt.

### RI-02 – Governed Risk Runs

- Quantifizierungs-/Aggregationsruns speichern Snapshot, Parameter, Seed,
  Korrelation, Modellversion und Ergebnis.
- Review und Publish erzeugen eine Risiko-Projektion.
- Abnahme: Gleiche Inputs erzeugen gleiche Resultate; ungültige Korrelationen
  und Double Counting brechen mit Erklärung ab.

### RI-03 – Entscheidungskette

- Risk-to-Plan-Integration und Mitigation-Referenzen zu Modul 06.
- Abnahme: Jede finanzielle Risikoauswirkung ist einmalig und periodengenau
  verknüpft; Control-Kosten und vermiedener Verlust bleiben getrennt.

### RI-04 – Optional: Market/Treasury Risk

- Erst mit belastbaren Marktzeitreihen und operationaler Kapazität einführen.
- Abnahme: Kein fortgeschrittenes Modell wird ohne dokumentierte Validierung
  und Backtest in eine Management-Ansicht übernommen.

## Definition of Done

Ein Betreiber kann die Top-Risiken, Limits und eine reproduzierbare
Risikoaggregation veröffentlichen. Markt-/Treasury-Risiko wird nur aktiviert,
wenn Datenversorgung und Modellgovernance tatsächlich betrieben werden können.
