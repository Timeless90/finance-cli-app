# Modul 03 – Cost & Profitability Management

## Value Proposition

Dieses Modul zeigt, welche Produkte, Kunden, Kanäle und Organisationseinheiten
Wert schaffen oder Marge vernichten. Es verhindert, dass Verrechnungen und
Sensitivitäten nur in individuellen Kalkulationstabellen existieren.

## Informationsfluss

```text
freigegebener GL-/Kosten-Snapshot + Dimensionsmapping
→ Kostenpools und Allokationsversion
→ Contribution Margin / Operating Margin
→ Sensitivität und Margin-at-Risk
→ veröffentlichter Profitability-Workspace
```

## Fachlicher Umfang

- Deckungsbeitrag I, Deckungsbeitrag II, Operating Margin und Margin-Prozent.
- Analyse nach Produkt, Kunde, Kanal, Cost Center und Profit Center.
- Direkte, treiberbasierte und Activity-Based-Costing-Allokationen.
- Versionierte Kostenpools, Treiber, Schlüssel und vollständige Abstimmung zum
  Quellbetrag.
- Preis-, Mengen-, variable- und fixe-Kosten-Sensitivität.
- Margin-at-Risk samt erwarteter Marge, Schwellenwert und
  Zielunterschreitungswahrscheinlichkeit.

## Bestehende Basis und Ziel-Lücken

Berechnungen, Allokationsabstimmung, Sensitivitäten und Margin-at-Risk sind als
Backend-Domain und API vorhanden. Für den Geschäftsprozess fehlen persistierte
Kostenmodelle, ein Approval-Lifecycle für Schlüssel sowie ein Live-Workspace,
der nicht nur aus Import-Standardwerten abgeleitet wird.

## Umsetzungsreihenfolge

### PR-01 – Dimensions- und Kostenbasis

- Aus Modul 00: Konten-, Produkt-, Kunden- und Kostenstellen-Mapping vollständig
  machen.
- Backend: versionierte Cost Pools und Allokationsschlüssel persistieren.
- Abnahme: Jeder verteilte Euro stimmt je Pool exakt gegen den Quell-Snapshot.

### PR-02 – Management-Profitability

- Backend: gespeicherte Summary-Runs und Publish in den Profitability-Workspace.
- Frontend: Ranking, Drill-down, Dimension-Filter und Datenlückenanzeigen.
- Abnahme: Eine Produktmarge lässt sich zu Umsatz, direkten Kosten,
  Allokationsversion und Quelle zurückführen.

### PR-03 – Steuerung und Risiken

- Sensitivitäts- und Margin-at-Risk-Runs mit Scenario, Seed und Modellversion.
- Übergabe eines genehmigten Margin-Risikos an Enterprise Risk oder Action
  Management als Referenz, niemals als kopierter Wert.
- Abnahme: Preis-/Kostenstress ist nachvollziehbar und kann eine Maßnahme
  begründen.

## Abhängigkeiten

Erfordert Modul 00 und nutzt Planning-Volumen/Preisannahmen aus Modul 01.
Performance konsumiert die veröffentlichten Margen; Liquidity nutzt bei Bedarf
Cash-Effekte, aber nicht die interne Allokationslogik.

## Definition of Done

Ein Betreiber kann einen Kostenpool zuordnen und freigeben, eine
Produkt-/Kundenprofitabilität veröffentlichen und eine auffällige Marge mit
Quellbetrag, Schlüssel und Sensitivität erklären.
