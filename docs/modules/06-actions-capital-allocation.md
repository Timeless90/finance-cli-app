# Modul 06 – Actions, Capital Allocation & Funding

## Value Proposition

Dieses Modul übersetzt Diagnose in eine explizite Entscheidung: Welche
Maßnahmen lohnen sich, wer liefert sie bis wann, wie wirken sie auf EBITDA,
Cash und Covenants – und welche Projekte bzw. Finanzierungen passen in die
verbleibende Kapazität?

## Informationsfluss

```text
Performance / Liquidity / Risk Signal → Action oder Projektentwurf
→ Wirkungssimulation / Bewertung → Review & Entscheidung
→ Umsetzung und Realized-vs-Planned → Command Center / Reporting
```

Actions und Capital bleiben getrennte Entitäten: eine operative Maßnahme ist
nicht automatisch ein Investitionsprojekt. Beide nutzen aber dieselben
Kontext-, Lineage- und Approval-Regeln.

## Fachlicher Umfang

- Maßnahmenkatalog mit Owner, Termin, Kosten, Confidence, Status und
  zeitindizierten EBITDA-, Cash- und Covenant-Effekten.
- `impact_key` verhindert Doppelzählung zwischen Maßnahmen und Risikoeffekten.
- Deterministische Priorisierung nach Nutzen/Kosten, Dringlichkeit und
  Constraints; Benefit Tracking misst Realized vs Planned.
- Projektbewertung mit NPV, IRR, ROIC und Payback; Monte-Carlo-NPV mit Seed,
  Szenario- und Risiko-Effekten.
- Portfoliooptimierung unter Budget, Cash-Headroom, Leverage und Interest-Cover.
- Funding-Szenarien für Erlös, Zins, Tilgung, Debt Service und Covenant-Effekt.

## Bestehende Basis und Ziel-Lücken

Action-Simulation/Priorisierung/Benefit-Tracking sowie Project Valuation,
Monte-Carlo, Portfolio-Optimierung und Funding-Evaluation existieren als
Calculation APIs. Der Produktworkflow braucht persistierte Drafts, sichere
Lifecycle-Übergänge, Idempotency, Review-/Approval, published decision
Read-Models und klare Referenzen auf statt frei eingegebener Finanzwerte.

## Umsetzungsreihenfolge

### AC-01 – Governed Action Management

- Persistente Maßnahmen mit Status `DRAFT → PLANNED → ACTIVE → COMPLETED` bzw.
  `BLOCKED/CANCELLED`, Owner, Review und Eskalation.
- Frontend: Maßnahmenliste, Statuswechsel, fällige/blockierte Aufgaben und
  Benefit-Tracking.
- Abnahme: Wiederholte Requests legen keine doppelte Maßnahme an; gesperrte oder
  überfällige Maßnahmen sind sichtbar.

### AC-02 – Wirkung und Priorisierung

- Wirkung bezieht sich auf veröffentlichte Forecast-/Liquidity-/Risk-Versionen.
- Backend prüft Scope, periodische Wirkung und `impact_key`.
- Abnahme: Ein Portfolio zeigt Bruttoeffekt, Kosten und netto nicht vermischte
  Wirkungen sowie jeden ausgeschlossenen Konflikt.

### AC-03 – Capital & Funding

- Projekte, Cashflows, Bewertungsruns und Portfolio-Constraints persistieren.
- Funding erst aktivieren, wenn Modul 04 Debt/Covenant-Daten veröffentlicht.
- Abnahme: Auswahl verletzt keinen Constraint; NPV/IRR und Unsicherheit sind
  mit Szenario, Seed und Quellversion nachvollziehbar.

## Abhängigkeiten

AC-01 kann nach Modul 00 und Command Center starten. AC-02 benötigt
Performance/Liquidity/Risk-Referenzen. AC-03 benötigt Liquidity und, für
risikoadjustierte Bewertung, Enterprise Risk. Das Modul schreibt niemals direkt
in einen Forecast; eine genehmigte Wirkung wird als neue Planungsannahme oder
Scenario-Referenz verarbeitet.

## Definition of Done

Ein Betreiber kann eine Entscheidung vom auslösenden Signal bis zu Owner,
finanzieller Wirkung, Freigabe und realisiertem Nutzen nachweisen.
