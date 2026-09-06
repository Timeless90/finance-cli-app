# Modul 08 – Governed Finance Copilot

## Value Proposition

Der Copilot erklärt freigegebene Finanzdaten in natürlicher Sprache, ohne eigene
Zahlen zu berechnen oder Entscheidungen auszuführen. Er verkürzt die Analyse
eines Einzelbetreibers, ersetzt aber weder Review noch Approval.

## Zielworkflow

```text
Frage + aktueller Scope → Autorisierungsprüfung → freigegebene Facts/Tools
→ Modellantwort mit Quellen → Numeric Grounding → Audit-Record
```

Das Frontend spricht nie direkt mit Foundry oder einem Modellanbieter. Das
Backend baut den Kontext, filtert Company-Scope, wählt eine Deployment-Alias und
prüft Antwort und Quellen.

## Fachlicher Umfang

- Grounded Summary für Command Center, Forecast, Liquidität und Risk.
- Explain Variance und Explain Risk über deterministische, zugelassene
  Read-/Analyse-Tools.
- Action-Empfehlungen nur aus vorhandenen Maßnahmen und Simulationen.
- Report-Entwürfe als unfreigegebener Text mit Quellenhinweisen.
- Sessions, Messages, Tool-Aufrufe, Modellroute, Quellen und Fehler als
  nachvollziehbare Interaktions-Lineage.
- Schutz vor Prompt Injection, Scope-Leakage und erfundenen Zahlen.

## Lokaler Betrieb

Der lokale Echo-Provider beantwortet eine Anfrage ohne externes Foundry-
Deployment. Damit testet der Betreiber Session, Scope, Quellenanzeige und
Fehlerzustände. Er erzeugt keine fachliche Analyse und darf nicht als
Produktions-KI ausgegeben werden.

## Bestehende Basis und Ziel-Lücken

Die Foundry-fähige Adaptergrenze, Deployment-Routing, Fallbacks,
approved-fact-only Grounding, Scope-Filter, Injection-Check, Numeric Grounding
und Audit-Records existieren bereits. Auszubauen sind persistierte Copilot-
Sessions, eine vollständige UI, Tool-Policy je Rolle und belastbare
Evaluation-Suites. Foundry selbst bleibt optional bis eine Azure Subscription
eingerichtet ist.

## Umsetzungsreihenfolge

### CO-01 – Lokaler, sicherer Erklärungspfad

- Sessions/Messages in PostgreSQL, Echo-Adapter als lokale Implementierung.
- Frontend: Kontext, Quellen, Modellstatus und klare Echo-Kennzeichnung.
- Abnahme: Eine Antwort enthält nur den erlaubten Scope; eine Cross-Company-
  Anfrage wird erklärt abgewiesen.

### CO-02 – Zugelassene Finanz-Tools

- Read-only Tools für genehmigte Workspace- und Run-Daten; keine Schreibtools.
- Testfälle für Injection, fehlende Quellen, nicht erlaubte Tools und
  ungrounded Zahlen.
- Abnahme: Jede finanzielle Zahl einer Antwort ist in der Quellenliste
  wiederzufinden oder die Antwort wird verworfen.

### CO-03 – Optional: Foundry-Einführung

- Erst nach Azure-/Identity-/Secret-Setup: Deployment-Aliasse, Evaluation,
  Kostenlimit und humaner Modellwechselprozess.
- Abnahme: Ein Modellwechsel erfolgt nur nach dokumentierter Evaluation und
  ändert keine Finanz- oder Berechtigungslogik.

## Abhängigkeiten

Benötigt Modul 00 und mindestens einen publizierten Read-Model-Produzenten.
Reporting kann Copilot-Drafts lesen, aber externe Reports bleiben menschlich
freizugeben. Der Copilot hat weder Approval- noch Buchungsberechtigungen.

## Definition of Done

Ein Betreiber kann eine Quellen-gebundene Frage stellen, die verwendeten Fakten
prüfen und sicher erkennen, ob die Antwort lokal emuliert oder durch ein
freigegebenes Modell erzeugt wurde.
