# Modul 01 – Planning & Forecast

## Zielbild und Value Proposition

Planning & Forecast gibt CFO, FP&A und den operativen Verantwortlichen eine
gemeinsame, nachvollziehbare Sicht auf die erwartete finanzielle Entwicklung.
Statt Werte in getrennten Dateien zu sammeln, werden operative Treiber,
Annahmen, Ist-Daten und Szenarien zu einem integrierten Forecast verbunden.

Das Modul beantwortet insbesondere diese Entscheidungen:

| Entscheidung | Fachliche Antwort des Moduls |
| --- | --- |
| Erreichen wir Umsatz-, EBITDA- und Cash-Ziele? | Deterministischer Forecast je Company, Periode und Szenario. |
| Warum verändert sich der Forecast? | Treiber, Annahmesatz, Daten-Snapshot und Vorgängerversion sind sichtbar. |
| Wie robust ist die Erwartung? | P10/P50/P90, Zielverfehlungswahrscheinlichkeit und Backtesting-Kennzahlen. |
| Was geschieht bei einer Abweichung? | Downside-/Upside-Szenarien, Schwellenwerte und kommentierbare Handlungsbedarfe. |
| Welcher Forecast ist verbindlich? | Backend-seitiger Review-, Freigabe- und Publish-Lifecycle mit unveränderlicher Version. |

Die Funktion wird zuerst für eine Gesellschaft und eine monatliche Planung
ausgeliefert. Konzernkonsolidierung, Intercompany-Eliminierung sowie detaillierte
Debt- und Covenant-Berechnungen bleiben in den Modulen Consolidation bzw.
Liquidity.

## Nutzer und Verantwortlichkeiten

| Rolle | Aufgabe | Berechtigung im Zielbild |
| --- | --- | --- |
| FP&A Planner | Treiber und Annahmen erfassen, Forecast-Entwurf erstellen | Entwurf anlegen und bearbeiten |
| Operative:r Owner | Umsatz-, Kosten- oder Workforce-Treiber verantworten | Zugewiesene Treiber vorschlagen bzw. bestätigen |
| Finance Controller | Datenabstimmung und Plausibilität prüfen | Review durchführen oder zurückweisen |
| CFO | Steuerungsentscheidung treffen | Forecast freigeben und publizieren |
| Leser:in | Ergebnisse nachvollziehen | Nur veröffentlichte Read-Models sehen |

Keine Browser-Rolle berechnet Finanzwerte selbst. Validierung, Berechnung,
Freigaben und Mandantenscope liegen im Backend.

## Fachlicher Informationsfluss

```text
ERP / Excel / CSV
  → geprüfter, freigegebener Daten-Snapshot
  → Ist-Werte und Plan-Baseline
  → Treiber + Annahmesatz + Szenario
  → integrierter Forecast-Run (P&L, Bilanz, Cashflow)
  → Review / Freigabe / Veröffentlichung
  → Planning-Read-Model → Live-API → Frontend
```

Jeder veröffentlichte Wert ist mindestens auf `company`, `period`, `scenario`,
`snapshot`, `assumption_set`, `model_version` und `forecast_version`
zurückführbar. Die bei der lokalen Datenimport-Strecke veröffentlichte
Finanzübersicht liefert derzeit die Ist-/Baseline-Daten; sie ist noch kein
treiberbasierter Forecast.

## Fachlicher Umfang

### 1. Ist-Daten und Plan-Baseline

- Nutzt ausschließlich einen genehmigten Daten-Snapshot aus dem Data-&-Governance-
  Prozess.
- Ordnet Konten den benötigten P&L-, Bilanz- und Cashflow-Positionen zu.
- Zeigt fehlende, nicht abgestimmte oder nicht freigegebene Quellen als Blocker.
- Enthält keine stillschweigende Ersetzung durch Mock-Daten oder Browserwerte.

### 2. Treiber und Annahmesätze

- Umsatz: Volumen, Preis, Conversion, Mix; später zusätzlich Backlog und Pipeline.
- Kosten: variable Kostenquote, fixe Betriebskosten, Personal und Abschreibungen.
- Workforce: Start-FTE, Einstellungen, Austritte, Durchschnittsgehalt und Oncost.
- Working Capital: DSO, DPO und Lagerreichweite; außerdem Capex, Steuersatz und
  Eröffnungswerte.
- Ein Annahmesatz ist versioniert, hat einen Owner, eine Gültigkeit und eine
  fachliche Begründung. Nach Veröffentlichung bleibt er unveränderlich.

### 3. Integrierter deterministischer Forecast

- Unterstützt Monats-Horizonte von 12, 18 und 24 Monaten.
- Rechnet Umsatz, variable/fixe Kosten, EBITDA, EBIT, Steuer und Net Income.
- Rollt Forderungen, Vorräte, Verbindlichkeiten, operativen Cashflow, Capex,
  Closing Cash und Equity fort.
- Prüft je Periode die mathematische Bilanzgleichung sowie die vollständige
  Abdeckung des gewählten Horizonts.
- Übernimmt beim Monatsabschluss die Ist-Periode, verlängert den Horizont und
  verknüpft die neue Version mit ihrer Vorgängerin.

### 4. Szenarien, Unsicherheit und Forecast Assurance

- Base, Upside und Downside sind getrennte, versionierte Szenarien im gleichen
  Company-/Period-Scope.
- Der probabilistische Overlay liefert bei reproduzierbarem Seed P10/P50/P90 für
  EBITDA, EBIT und Cashflow. Student-t ist der Standard; Block-Bootstrap und
  Regime-Modelle sind fortgeschrittene, ausdrücklich gewählte Methoden.
- Backtesting erfolgt rolling-origin und ohne Zukunftsdaten. Das Modul zeigt
  mindestens MAE, WAPE, Bias, Interval Coverage und Log Score.
- Schwellenwerte für Ziele, Warnungen und Breaches zeigen auch eine
  Zielverfehlungs- bzw. Überschreitungswahrscheinlichkeit.

### 5. Governance und Veröffentlichung

```text
DRAFT → IN_REVIEW → APPROVED → PUBLISHED
  ↑          │            │
  └─ RETURNED┘            └─ nur als neue, abgeleitete Version ändern
```

- Die Person, die einen Entwurf erstellt hat, darf ihn nicht selbst freigeben.
- Eine Veröffentlichung erzeugt ein unveränderliches Read-Model je
  Company/Period/Scenario.
- Ein neuer Forecast ändert nie eine bereits veröffentlichte Version, sondern
  erzeugt eine nachverfolgbare Nachfolgeversion.
- Nicht veröffentlichte oder fremde Scopes liefern im Frontend einen expliziten
  Empty-/Access-State, niemals Zahlen aus einem anderen Kontext.

## Bestehende Basis und Lücken

| Bereich | Bereits vorhanden | Als Nächstes zu implementieren |
| --- | --- | --- |
| Rechenmodell | Integriertes deterministisches P&L-/Bilanz-/Cashflow-Modell | Kontenzuordnung aus freigegebenen Snapshots und fachlich verwaltete Treiber |
| Forecast-Version | 12/18/24 Monate, Lineage und Close-Refresh im Domain-Service | PostgreSQL-Repository, Lifecycle, Autorisierung und Concurrency |
| Unsicherheit | Probabilistische Simulation, Backtest, Schwellenbewertung | Persistierte Runs, reproduzierbare Inputs und Darstellung der Ergebnisse |
| API | Berechnungsendpunkte für Forecast, Probability, Backtest und Thresholds | Ressourcen-APIs für Treiber/Annahmen/Versionen sowie Review/Approve/Publish |
| Frontend | Live-Lesen eines veröffentlichten Planning-Workspaces | Eingabe- und Review-Flows; Run-Status; versionierte Drill-downs |
| Lokale Datenbasis | Import, Validierung, Snapshot und Publish in PostgreSQL/local storage | Semantische Mapping-Regeln von Snapshot-Konten zu Planning-Baseline |

Die bestehenden Berechnungsendpunkte bleiben als technische Grundlage erhalten.
Die Eingabe kompletter fachlicher Werte aus dem Browser wird jedoch nicht zum
Produktworkflow ausgebaut: Das Backend lädt künftig den freigegebenen Snapshot
und die gespeicherten Annahmen selbst.

## Implementierungsschnitte

### PF-01 – Planning Baseline aus freigegebenem Snapshot

**Outcome:** Für eine Company und einen Monats-Scope ist eindeutig, welche
Ist-Werte und welche Kontenzuordnung den Forecast speisen.

- Backend: Planning-Baseline- und Account-Mapping-Modelle, PostgreSQL-
  Repositories, Validierung von Vollständigkeit und Bilanzabstimmung.
- API: Baseline lesen; Mapping-Vorschlag speichern, prüfen und freigeben.
- Frontend: Baseline-Status, fehlende Kontenzuordnungen und Snapshot-Lineage im
  Planning-Workspace zeigen.
- Abnahme: Ein freigegebener Import kann ohne freie Finanzwerte im Browser als
  Baseline referenziert werden; unvollständige Mappings blockieren den Run.

### PF-02 – Treiber und Annahmesätze

**Outcome:** FP&A verwaltet nachvollziehbare Treiber statt periodische
Gesamtergebnisse zu kopieren.

- Backend: Versionierte Driver- und Assumption-Set-Entitäten mit Owner, Scope,
  Gültigkeit, Begründung und Audit-Ereignissen.
- API: Draft erstellen/ändern, zur Prüfung einreichen und freigegeben lesen.
- Frontend: Eingabemasken nach Treiberart, Validierungsfehler, Änderungsvergleich
  und Owner-Status.
- Abnahme: Jede Forecast-Version referenziert genau einen unveränderlichen,
  genehmigten Annahmesatz; ungültige Quoten, negative Mengen und Lücken werden
  serverseitig abgewiesen.

### PF-03 – Deterministischer Forecast und Versionsworkflow

**Outcome:** Ein genehmigter Annahmesatz erzeugt eine überprüfbare Forecast-
Version und ein publiziertes Planning-Read-Model.

- Backend: Persistierte Forecast-Runs, idempotenter Start, Status, Ergebnisse,
  Review/Approve/Publish und Optimistic Concurrency.
- API: Run starten und lesen; Review, Freigabe, Veröffentlichung; Versionen und
  Vorgänger abrufen.
- Frontend: Run starten, Fortschritt/Fehler anzeigen, Statement- und Cashflow-
  Drill-down, Review- und Freigabeaktionen.
- Abnahme: Ein CFO kann nur einen geprüften Run veröffentlichen; der Workspace
  zeigt danach ausschließlich dessen Werte und vollständige Lineage.

### PF-04 – Szenarien, Wahrscheinlichkeiten und Assurance

**Outcome:** Die Steuerung sieht Ergebnisbandbreiten und die historische Güte
statt einer einzelnen Punktprognose.

- Backend: Persistierte probabilistische Runs, Seeds, Parameter, Backtests und
  Threshold-Evaluierungen pro Forecast-Version.
- Frontend: Base/Upside/Downside-Vergleich, P10/P50/P90-Korridor,
  Zielverfehlungswahrscheinlichkeit und Assurance-Drill-down.
- Abnahme: Gleiche Version, Parameter und Seed liefern dasselbe Ergebnis;
  fehlende oder unzureichende historische Daten werden erklärbar ausgewiesen.

### PF-05 – Monatsabschluss und operativer Betrieb

**Outcome:** Der Forecast wird monatlich sicher fortgeschrieben.

- Backend: Close-Refresh aus dem nächsten freigegebenen Snapshot, Scheduler/Job-
  Ausführung, Audit, Monitoring und Wiederanlauf.
- Frontend: Abschluss-Checkliste, Vergleich alter/neuer Version, Eingriff bei
  Blockern.
- Abnahme: Der Monatsabschluss erzeugt eine Nachfolgeversion mit verlängertem
  Horizont, ohne die zuvor publizierte Version zu verändern.

## Ziel-API (ergänzend, noch nicht implementiert)

Die konkreten Pydantic-Modelle werden vor PF-01 über OpenAPI festgelegt. Die
fachlichen Ressourcen sind:

- `planning/baselines` für Snapshot-Kontenzuordnung und Baseline-Status;
- `planning/assumption-sets` und `planning/drivers` für versionierte Eingaben;
- `planning/forecast-runs` für Start, Status, Ergebnis und Lineage;
- explizite Lifecycle-Aktionen `review`, `approve`, `publish` auf zulässigen
  Ressourcen;
- `planning/workspace` als ausschließlich lesbares, veröffentlichtes
  Frontend-Read-Model.

Alle Schreiboperationen prüfen Mandantenscope, Rolle, Versionskonflikte und –
wo Wiederholung möglich ist – einen `Idempotency-Key`. Nach jeder
Contract-Änderung werden OpenAPI-Typen mittels `npm run api:sync` regeneriert;
MSW-Fixtures bleiben strukturell gleich.

## Release-Gates

- Backend: Domänen- und API-Tests für Berechnung, Scope, Rollen, Lifecycle,
  Idempotenz und Lineage; Migrationstest gegen PostgreSQL.
- Frontend: generierter Contract, Unit-Tests für Adapter und Zustände sowie ein
  Live-API-Playwright-Flow von Baseline über Freigabe bis zum publizierten
  Workspace.
- UAT: Nicht-personenbezogener Beispielsdatensatz inklusive Base-/Downside-
  Szenario; dokumentierte Evidenz für einen erfolgreichen sowie einen bewusst
  abgelehnten Durchlauf.

## Definition of Done für den ersten nutzbaren Planning-Release

Ein FP&A Planner kann einen freigegebenen Daten-Snapshot als Baseline nutzen,
einen Annahmesatz als Entwurf pflegen und einen Forecast-Run anstoßen. Ein
Controller prüft ihn, ein CFO veröffentlicht ihn. Danach sieht ein berechtigter
Nutzer im Frontend nur die veröffentlichte Version mit Statement, Forecast-
Korridor, Treibern und vollständiger Herkunft. Fehlende Freigaben, fehlende
Mappings, fremde Companies und Berechnungsfehler sind sichtbar, verständlich und
führen nie zu Mock- oder Fallback-Zahlen.
