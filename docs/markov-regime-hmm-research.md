# Markov-Regime-Switching: Methodik und Implementierungsentscheidung

## Ziel

Das Advanced Feature modelliert zusammenhängende ruhige und turbulente Marktphasen. Es ergänzt die bestehenden iid- und Bootstrap-Modelle und ist insbesondere für Drawdowns, Krisendauer, Sequence-of-Returns-Risk und Stressszenarien gedacht.

## Modell

Für monatliche Log-Renditen `r_t` und einen latenten Zustand `S_t` gilt:

```text
P(S_t = j | S_(t-1) = i) = p_ij
r_t | S_t = k ~ F(mu_k, sigma_k)
```

Die erste produktive Version verwendet genau zwei Zustände. Nach jedem Fit werden die Zustände deterministisch nach ihrer Volatilität sortiert:

- Zustand 0: niedrigere Volatilität, Label `normal`
- Zustand 1: höhere Volatilität, Label `crisis`

Damit wird Label Switching über Fits und Rolling Windows kontrolliert.

## Schätzung

Die Kalibrierung verwendet Maximum-Likelihood-Schätzung über ein Forward-Backward-Verfahren und EM-Updates. Mehrere unabhängige Initialisierungen reduzieren das Risiko lokaler Optima. Ausgewählt wird der Fit mit der höchsten endlichen Log-Likelihood.

Unterstützte Emissionen:

- Gaussian: empfohlene produktive Baseline
- Student-t mit gemeinsamem Freiheitsgrad: experimentelle Heavy-Tail-Variante

Ein gemeinsamer Student-t-Freiheitsgrad vermeidet zusätzliche schwach identifizierte Parameter bei typischen monatlichen ETF-Stichproben.

## Datenanforderungen

Technisches Minimum: 120 Monatsrenditen.

Empfohlene produktive Untergrenze: 180 bis 240 Monatsrenditen. Bevorzugt wird eine lange Total-Return-, Net-Total-Return- oder Adjusted-Price-Reihe des zugrunde liegenden Index. Kurze ETF-Historien enthalten häufig zu wenige Marktzyklen für stabile Regimeparameter.

Extremwerte werden nicht pauschal winsorisiert. Sie tragen wesentliche Information über das Hochvolatilitätsregime. Nur nachweisliche Datenfehler sollten korrigiert werden.

## Modellselektion und Validierung

AIC und BIC werden exportiert. Sie reichen allein nicht zur Freigabe des Modells aus. Ein Regime-Modell sollte nur als bessere Alternative gelten, wenn es zusätzlich in Rolling-Origin-Tests überzeugt.

Empfohlene Prüfungen:

1. Out-of-sample Log Score
2. Coverage und Intervallbreite
3. VaR-Überschreitungen
4. Stabilität von Mittelwerten, Volatilitäten und Übergangswahrscheinlichkeiten
5. Mindestbelegung beider Regime
6. plausible erwartete Regimedauern
7. Vergleich mit Student-t iid und Moving Block Bootstrap

Ein gewöhnlicher Likelihood-Ratio-Test zwischen einem Ein- und Zwei-Regime-Modell darf nicht mit der üblichen Chi-Quadrat-Referenzverteilung interpretiert werden, weil Parameter unter der Nullhypothese nicht identifiziert sind. Für formale GOF- oder LR-Tests ist ein parametrischer Bootstrap mit vollständiger Neuschätzung je Replikat erforderlich.

## Reproduzierbarkeit

Die Simulation verwendet `numpy.random.SeedSequence.spawn`. Unabhängige Zufallsströme werden aus einem Root-Seed erzeugt. Identische Pfade setzen voraus:

- gleichen Root-Seed
- gleiche Anzahl paralleler Streams
- gleiche Pfad- und Monatsanzahl
- gleiche NumPy-Version

Die Streamanzahl wird deshalb in der Konfiguration und im Run-Manifest gespeichert.

## Stressparameter

Das Regime-Modell unterstützt:

- Start im Normal- oder Krisenregime
- explizite Krisenstartwahrscheinlichkeit
- Override der Krisenpersistenz
- Multiplikator für den Übergang von Normal zu Krise

Diese Werte verändern nur das Szenario, nicht die gespeicherte historische Kalibrierung.

## Einsatzempfehlung

`student_t` bleibt das einfachere Standardmodell für langfristige Endwertplanung. `markov_regime` ist besonders geeignet für:

- realistische Krisencluster
- Maximum Drawdown und Ulcer Index
- Sequence-of-Returns-Risk
- Entnahme- und Rentenmodelle
- Krisen- und Persistenz-Stresstests

Das Modell sollte nicht produktiv verwendet werden, wenn ein Regime nur wenige Beobachtungen erhält, Übergangswahrscheinlichkeiten an den Rand laufen oder Rolling-Fits stark instabil sind.

## Quellenbasis

Die Implementierungsentscheidung folgt insbesondere:

- Hamiltons klassischem Markov-Switching-Ansatz
- Forschung zu Identifizierbarkeit und Label Switching in latenten Zustandsmodellen
- Best Practices für parametrische Monte-Carlo-GOF-Tests bei geschätzten Parametern
- NumPy-Empfehlungen für unabhängige parallele Zufallsströme

Die vollständige Deep-Research-Auswertung wurde vor der Implementierung durchgeführt; dieses Dokument hält die für den Code verbindlichen Entscheidungen und Grenzen fest.
