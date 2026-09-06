# Modul 04 – Cash, Liquidity & Covenant Control

## Value Proposition

Liquidity Control macht aus integrierten Planwerten eine operative
Frühwarnung: Wann fällt Cash unter die Mindestliquidität, wann entsteht ein
Funding Gap und wie nahe ist eine Covenant-Verletzung?

## Informationsfluss

```text
Bank / AR / AP / Payroll / Tax / Capex + Planning-Cashflow + Debt-Daten
→ 13-Wochen- und Monatsforecast → Stress / Funding-Szenario
→ Covenant-Headroom → veröffentlichter Liquidity-Workspace
```

## Fachlicher Umfang

- Direkter wöchentlicher 13-Wochen-Cash-Forecast inklusive Roll-forward der
  Bankbestände.
- Monatlicher 12- bis 24-Monats-Forecast aus Operating-, Investing- und
  Financing-Cashflows.
- Working Capital mit DSO, DPO, DIO und Zahlungsprofilen.
- Instrumentgenauer Debt Schedule für Zins, Tilgung, Laufzeit, Limits und
  Refinanzierung.
- Covenant-Engine für Leverage, Interest Cover und vertraglich definierte
  Formeln einschließlich Headroom und Breach-Wahrscheinlichkeit.
- Stressfälle: Umsatzrückgang, Collection Delay, Kostenanstieg,
  Refinanzierungsschock und Gegenmaßnahmen.

## Bestehende Basis und Ziel-Lücken

Die Berechnungs-APIs für Cash Forecasts, Working Capital, Debt Schedule,
Covenants, Stress und Accuracy existieren. Es fehlt ein persistiertes
Cash-Input-Ledger (vor allem Bank, offene Posten und Debt-Verträge), der
Review-/Publish-Workflow sowie die fachlich vollständige Integration aus
Planning und Actions.

## Umsetzungsreihenfolge

### LI-01 – 13-Wochen-Cash als minimaler Nutzen

- Backend: persistierte Wochen-Cash-Inputs und Bank-Reconciliation gegen den
  freigegebenen Snapshot.
- Frontend: Cash-Kalender, Minimum-Cash, Funding-Gap und Datenqualitätsblocker.
- Abnahme: Jede Woche beginnt mit dem Closing Cash der Vorwoche; Abweichungen
  zum Bankwert sind sichtbar.

### LI-02 – Debt und Covenants

- Vertrags- und Instrumentdaten mit Freigabe, Formelversion und Fälligkeiten.
- Backend berechnet Headroom und simulierte Breach-Wahrscheinlichkeit.
- Abnahme: Ein negativer Headroom zeigt Formel, Inputversion, Fälligkeit und
  verantwortliche Gegenmaßnahme.

### LI-03 – Integrierte Szenarien

- Planning- und Action-Effekte über versionierte Referenzen einbeziehen.
- Stress- und Funding-Runs persistieren, freigeben und publizieren.
- Abnahme: Ein Downside-Scenario ändert Cash und Covenants konsistent, ohne
  Werte im Frontend nachzurechnen.

## Abhängigkeiten

Erfordert Modul 00. LI-01 ist unabhängig von voll ausgebautem Planning möglich;
LI-03 benötigt Modul 01. Modul 06 referenziert Liquidity für
Maßnahmenwirkungen; Modul 07 verarbeitet diese Ergebnisse nur als genehmigte
Report-Werte.

## Definition of Done

Ein Betreiber sieht wöchentlich Bankabstimmung, Mindestliquidität und Funding
Gap; ein Covenant-Breach ist mit Vertragsformel, Herkunft und nächster
Entscheidung nachvollziehbar.
