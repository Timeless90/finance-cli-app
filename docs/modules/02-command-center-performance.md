# Modul 02 – CFO Command Center & Performance

## Value Proposition

Das Command Center beantwortet in wenigen Minuten: *Was ist passiert, warum
und wo muss entschieden werden?* Es verbindet veröffentlichte Ist-, Plan- und
Forecast-Werte, ohne eine zweite Rechenlogik im Browser zu schaffen.

## Nutzerfluss

```text
publizierter Snapshot / Forecast → KPI- und Variance-Read-Model
→ Command Center → Drill-down in Planning, Profitability, Liquidity oder Risk
→ Kommentar bzw. Maßnahme
```

Der globale Company-/Period-/Scenario-Kontext ist für alle Kacheln verbindlich.
Ein Kontextwechsel lädt ausschließlich den korrespondierenden Live-Read-Model;
fehlende Projektionen sind ein Empty-State, nicht ein Wert von null.

## Fachlicher Umfang

- Executive KPIs: Umsatz, EBITDA, EBIT, Free Cash Flow, Liquidität und Risiko-
  Signale mit Stand, Trend und Datenherkunft.
- KPI-Tree: additiv nachvollziehbare Hierarchie bis zu Segment, Produkt,
  Cost Center oder Profit Center.
- Varianzbrücken: Plan-Ist, Forecast-Ist und Forecast-Forecast; Preis, Menge,
  Mix, Kosten und Working Capital erklären die gesamte Abweichung.
- Forecast Assurance: MAE, WAPE, Bias, Coverage und Modell-/Horizont-Slice.
- Anomalien und Commentary: materialisierte Abweichungen fordern eine Erklärung
  mit Owner und optionaler Maßnahme.

## Bestehende Basis und Ziel-Lücken

Die API kann KPI-Trees, vollständig erklärte Varianzbrücken, Accuracy-Slices,
Anomalien und Commentary-Anforderungen berechnen. Das Frontend liest bereits
eine veröffentlichte Performance-Projektion. Noch zu produktisieren sind
persistierte Kommentare, Drill-down-Links in echte Quell- bzw. Run-Details und
ein Publish-Prozess, der die Berechnung aus genehmigten Quellen auslöst.

## Umsetzungsreihenfolge

### CP-01 – Verlässliches Executive Read-Model

- Backend: Command-Center-/Performance-Projektion mit As-of, Snapshot, Run- und
  Context-Lineage; Aktualisierung nur beim Publish.
- Frontend: KPI-Karten, leere/fehlende Zustände und direkte Links zur Quelle.
- Abnahme: Jede Kachel zeigt denselben Company-/Period-/Scenario-Scope und
  verweist auf eine veröffentlichte Quelle.

### CP-02 – Erklärbare Varianz

- Backend: gespeicherte Bridge-Inputs und die harte Null-Prüfung auf
  unerklärte Restabweichung.
- Frontend: Drill-down vom KPI zur Bridge, zu Dimensionen und Kommentar.
- Abnahme: Eine ausgewiesene Abweichung ist zu 100 Prozent durch belegte
  Beiträge erklärt oder als Datenlücke markiert.

### CP-03 – Steuerungsroutine

- Materiality-Regeln erzeugen Commentary-Aufgaben, nicht bloß Warnfarben.
- Kommentare verweisen auf Risiken oder Maßnahmen, ohne deren Werte zu kopieren.
- Abnahme: Eine signifikante Abweichung ist bis zu Owner, Frist und
  Entscheidungsstatus nachvollziehbar.

## Abhängigkeiten und Grenzen

Voraussetzung sind Modul 00 und veröffentlichte Planning-/Ist-Daten. Das Modul
orchestriert keine Forecasts, Allokationen oder Risiko-Simulationen; es liest
deren genehmigte Ergebnisse. Dadurch bleibt es als erstes tägliches Dashboard
für einen Einzelbetreiber schnell und zuverlässig.

## Definition of Done

Nach einem Publish sieht der CFO die wichtigsten Kennzahlen, kann eine rote
Kennzahl bis zur voll erklärten Varianz zurückverfolgen und erkennt klar, ob
eine Kommentierung oder weitere Entscheidung offen ist.
