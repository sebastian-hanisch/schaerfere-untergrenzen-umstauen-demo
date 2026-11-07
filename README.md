# Schärfere Untergrenzen: die Lücke schließen – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-schaerfere-untergrenzen-umstauen-demo.streamlit.app/)**

Neuntes Stück der Konzepte-Reihe **„Umstauen: Untergrenze und Suche“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. [Stück 2](https://sebastianhanisch-untergrenze-umstauen-demo.streamlit.app/) hat die **Untergrenze** gebaut: Jeder **Blocker** (ein Container über einem früher abzurufenden) muss mindestens einmal bewegt werden. Sie übersieht, dass ein Blocker oft **keinen sicheren Platz** findet und ein zweites Mal bewegt werden muss. Dieses Stück baut **vier Schranken** (LB1 bis LB4), rechnet sie live auf kleinen Buchten und misst vorberechnet, **wie oft sie das Optimum treffen**, **wie weit die Lücke schrumpft** und **was die Suche davon hat**.

## Warum dieses Problem

Eine Untergrenze entscheidet, wie viel eine Suche beschneiden kann, und sie beweist ohne Suche, dass eine Regel optimal ist. Die einfache Zählung ist billig, lässt aber bei 3 und 4 Lagen eine Lücke von im Mittel 1,3 bis 3,2 Hüben. Hier die Messung, wie weit eine **Zählung der Blocker ohne sicheren Stapel** (LB2) diese Lücke schließt, was eine **Platzplanung** (LB3) und **ein Abrufschritt Vorausschau** (LB4) zusätzlich bringen und was das je Suchknoten kostet. Ergebnis: Bei **zwei Lagen** schließt LB2 die Lücke fast vollständig (in 2 019 von 2 020 geprüften Buchten gleich dem Optimum), bei drei Lagen zur Hälfte. Mehr Schärfe spart Knoten, aber **nicht Zeit**: Nur LB2 spart Knoten **und** Zeit.

## Die Schranken

**Eigene Konstruktion** im Sinn der Konfliktzählung; die Zählung „kein sicherer Stapel“ steht dem Stand der Technik nahe (IDA\* beim Relocation-Problem, Zhu u. a. 2012; aus dem Gedächtnis zugeordnet, **nicht gelesen**). LB3 und LB4 sind eigene Bausteine. Alle vier sind **zulässig** (nie über dem Optimum des Zustands) und gelten in jedem Suchknoten.

Zustand = Bucht nach dem Abruf; nächster Abruf *t* im Stapel *i*; *B* die Container über *t* (oben zuerst); *m*<sub>*k*</sub> die früheste Abrufnummer im Stapel *k* (leer: unendlich).

- **LB1** (Stück 2): Zahl der Blocker.
- **LB2:** LB1 plus die Zahl der *c* in *B* mit *c* > max<sub>*k* ≠ *i*</sub> *m*<sub>*k*</sub>. Beweis: Jedes solche *c* muss auf einen Stapel *k* ≠ *i*, auf dem schon ein früher abzurufender Container liegt (Stapelminima sinken nur durch Aufsetzen); danach blockiert *c* erneut und muss ein zweites Mal bewegt werden. Dieser zweite Hub ist verschieden vom ersten Hub von *c* und von jedem Hub eines anderen Containers.
- **LB3:** wie LB2, aber die Platzierungen der Container in *B* werden der Reihe nach gewählt (oben zuerst, nur Stapel mit Platz): LB1 plus das Minimum der Zahl der Platzierungen auf einen Stapel mit früherem Container. Wer zuerst gesetzt wird, senkt das Minimum seines Stapels; volle Stapel scheiden aus. LB3 ≥ LB2.
- **LB4:** ein Abrufschritt Vorausschau: |*B*| plus das Minimum über alle Platzierungen von LB2 des Zustands nach dem Abruf. LB4 ≥ LB3.
- **Suche:** IDA\* mit Zustandsmerken (Stück 5 und 6), die Untergrenze ist austauschbar; Knoten = Aufrufe der Suche.

## Methodik

- **Live:** Die vier Schranken und die Suche mit jeder laufen live. Die Suche mit LB2 liefert den Bezugswert (Knotenlimit 300 000); die anderen drei laufen mit Limit 40 000 Knoten. Bei Limit gibt es **keinen** Wert, die Demo behauptet keinen.
- **Vorberechnet** (`sgu_bands.json`, erzeugt von `generate_precomputed.py`, einige Minuten in mehreren Prozessen): Stärke der Schranken in acht Zellen (3 × 2 bis 5 × 4, je 100 Buchten), Fehlschläge bei zwei Lagen (alle 120 Buchten 3 × 2 bis auf Vertauschen der Stapel; 1 500, 300 und 100 Zufallsbuchten mit 4, 5 und 6 Stapeln), Suche mit jeder Schranke in fünf Zellen (100 bis 40 Buchten). **Dieselben festen Buchten wie in Stück 4 bis 8** (Seeds ab 0, Platz 2); bei zwei Lagen Seeds ab 1000.
- **Alle Zeiten sind Einzelmessungen** (Python, Windows, die Zellen liefen in getrennten Prozessen nebeneinander) und schwanken.
- **Abschnitte der App:** Ergebnis (live); die Schranke von Hand; wie oft sie das Optimum trifft; zwei Lagen; was die Suche davon hat; Grenzen; mathematische Formulierung.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an festen Buchten, nachgerechnet in `tests/test_claims.py`, `tests/test_presets.py` und `tests/test_oracle_schaerfere_untergrenzen_umstauen.py`. **Zeiten sind die gespeicherten Einzelmessungen.**

**A: Wie oft trifft die Schranke das Optimum?** (je 100 Buchten, Platz 2; Optimum aus der Suche; Lücke = Optimum − Schranke, Mittel / Maximum)

| Zelle | Optimum Mittel | LB1 trifft | LB2 trifft | LB3 trifft | LB4 trifft | Lücke LB1 | Lücke LB2 | Lücke LB4 |
|---|---|---|---|---|---|---|---|---|
| 3 × 2 | 1,74 | 67 | 100 | 100 | 100 | 0,33 / 1 | 0 / 0 | 0 / 0 |
| 4 × 2 | 2,25 | 70 | 100 | 100 | 100 | 0,3 / 1 | 0 / 0 | 0 / 0 |
| 3 × 3 | 5,05 | 19 | 57 | 59 | 73 | 1,52 / 4 | 0,64 / 3 | 0,34 / 2 |
| 4 × 3 | 5,81 | 20 | 63 | 66 | 80 | 1,28 / 4 | 0,46 / 3 | 0,22 / 2 |
| 5 × 3 | 6,94 | 25 | 65 | 65 | 76 | 1,25 / 4 | 0,43 / 3 | 0,26 / 2 |
| 3 × 4 | 8,92 | 1 | 20 | 20 | 32 | 3,24 / 8 | 1,83 / 5 | 1,28 / 5 |
| 4 × 4 | 10,44 | 4 | 24 | 24 | 37 | 3 / 7 | 1,56 / 5 | 1,04 / 4 |
| 5 × 4 | 12,52 | 3 | 19 | 19 | 28 | 3,03 / 7 | 1,78 / 6 | 1,24 / 5 |

**Keine** Schranke liegt in einer gespeicherten Bucht über dem Optimum (zulässig, 800 von 800 Buchten).

**B: Zwei Lagen** (in wie vielen Buchten verfehlt die Schranke das Optimum?)

| Zelle (Buchten) | LB1 verfehlt | LB2 verfehlt | LB3 verfehlt | LB4 verfehlt |
|---|---|---|---|---|
| 3 × 2, alle (120) | 44 | 1 | 1 | 1 |
| 4 × 2 (1 500) | 489 | 0 | 0 | 0 |
| 5 × 2 (300) | 86 | 0 | 0 | 0 |
| 6 × 2 (100) | 26 | 0 | 0 | 0 |

Der eine Fehlschlag von LB2: die Bucht (1, 5), (3, 6), (4, 2) mit Höchsthöhe 4 (LB1 2, LB2 bis LB4 3, Optimum 4).

**C: Suche mit der jeweiligen Schranke** (IDA\* mit Zustandsmerken, Knotenlimit 1 Mio., kein Lauf am Limit; Knoten Median / Maximum, darunter die Zeit Median je Bucht)

| Zelle (Buchten) | LB1 | LB2 | LB3 | LB4 |
|---|---|---|---|---|
| 3 × 3 (100) | 16 / 123 | 8 / 70 | 8 / 45 | 6 / 36 |
| | 0,3 ms | 0,2 ms | 0,4 ms | 0,5 ms |
| 4 × 3 (100) | 14 / 367 | 8 / 158 | 8 / 143 | 7 / 68 |
| | 0,3 ms | 0,2 ms | 0,5 ms | 0,9 ms |
| 5 × 3 (60) | 27,5 / 734 | 10 / 449 | 10 / 302 | 9 / 161 |
| | 0,5 ms | 0,3 ms | 0,7 ms | 2,1 ms |
| 4 × 4 (60) | 173,5 / 7 168 | 84 / 2 608 | 70 / 2 429 | 43 / 737 |
| | 1,7 ms | 1,3 ms | 3,4 ms | 6,6 ms |
| 5 × 4 (40) | 284 / 56 710 | 134,5 / 28 017 | 120,5 / 26 641 | 56 / 11 239 |
| | 5,5 ms | 4,0 ms | 13,8 ms | 31,6 ms |

Summe der Zeit über die 40 Buchten 5 × 4: LB1 2,55 s, LB2 1,86 s, LB3 10,9 s, LB4 29,7 s. Alle Läufe einer Bucht finden dasselbe Optimum.

| Frage | Befund |
|---|---|
| **Sind die Schranken zulässig?** | Ja: Kein Zustand in 1 246 geprüften Zuständen (Phase 0) und in allen im Test unabhängig gerechneten Zuständen (alle aus den 120 Buchten 3 × 2 erreichbaren sowie Stichproben aus 4 × 2, 3 × 3 und 4 × 3) liegt über dem Restoptimum; LB1 ≤ LB2 ≤ LB3 ≤ LB4 überall. |
| **Wie weit schließt die Zählung ohne sicheren Stapel die Lücke?** | Bei zwei Lagen fast vollständig: LB2 trifft in 2 019 von 2 020 Buchten, LB1 nur in 1 375 (rund zwei von drei). Bei drei Lagen trifft LB2 in 57 bis 65 von 100 Buchten gegen 19 bis 25 mit LB1, bei vier Lagen in 19 bis 24 gegen 1 bis 4; die mittlere Lücke sinkt von 1,25 bis 1,52 auf 0,43 bis 0,64 (drei Lagen) und von 3,0 bis 3,24 auf 1,56 bis 1,83 (vier Lagen). |
| **Was bringt die Platzplanung (LB3)?** | Wenig: 59 gegen 57 (3 × 3), 66 gegen 63 (4 × 3), sonst gleich viele Treffer wie LB2. |
| **Was bringt die Vorausschau (LB4)?** | Mehr: 73 gegen 57 (3 × 3), 80 gegen 63 (4 × 3), 76 gegen 65 (5 × 3), 32 gegen 20 (3 × 4), 37 gegen 24 (4 × 4), 28 gegen 19 (5 × 4) Treffer. |
| **Bleibt eine Lücke?** | Ja, bei drei und vier Lagen: auch LB4 trifft nur in 28 bis 80 von 100 Buchten. Die Lücke kommt aus Mehrfachhüben, die erst spätere Abrufschritte erzwingen (Preset „Die Lücke bleibt“: alle vier Schranken 5, Optimum 6). |
| **Was hat die Suche davon?** | LB2 halbiert im Median die Knoten (zum Beispiel 16 auf 8, 284 auf 134,5) und ist in jeder Zelle **nicht langsamer** als LB1 (0,2 gegen 0,3 ms bis 4,0 gegen 5,5 ms). LB4 spart weitere Knoten (5 × 4: auf ein Fünftel von LB1), kostet bei 4 × 4 und 5 × 4 aber ein Mehrfaches der Zeit (5 × 4: 31,6 gegen 5,5 ms im Median). LB3 spart kaum Knoten gegenüber LB2 und kostet mehr Zeit. |

**Presets** (Eigenschaften in `tests/test_presets.py`): „Alltag“ (3 × 3, Bucht 12: LB1 bis LB3 4, LB4 und Optimum 5), „Zwei Lagen: LB2 reicht“ (4 × 2, Bucht 3: LB1 2, LB2 und Optimum 3), „LB2 schließt die Lücke“ (4 × 4, Bucht 0: LB1 7, LB2 und Optimum 10), „Die Lücke bleibt“ (3 × 3, Bucht 27: alle 5, Optimum 6), „LB2 verfehlt“ (3 × 2, Bucht 100: LB2 3, Optimum 4), „Schärfer lohnt nicht“ (5 × 4, Bucht 0: weniger Knoten mit jeder Stufe, Optimum 18).

**Korrektur gegenüber dem Plan:** Die Zählungen (Treffer, Lücken, Fehlschläge, Knotenzahlen) stimmen mit der Vormessung überein. Die **Zeiten** weichen ab, weil die Zellen der Messung nebeneinander in mehreren Prozessen liefen: bei 5 × 4 Median 5,5 / 4,0 / 13,8 / 31,6 ms (Plan 2,9 / 1,8 / 7,2 / 16,5 ms), Summe 2,55 / 1,86 / 10,9 / 29,7 s (Plan 1,5 / 1,1 / 6,1 / 20,9 s); die **Verhältnisse** (LB2 schneller als LB1, LB3 und LB4 deutlich langsamer) tragen in beiden Läufen. Die Plan-Aussage „LB3 und LB4 sparen Knoten, aber keine Zeit“ gilt für LB3 und LB4; bei LB3 sind es kaum Knoten.

## Ehrliche Grenzen

- **Nur ein Abrufschritt Vorausschau.** LB5 und tiefer sind nicht gemessen; die Lücke bleibt bei drei und vier Lagen.
- **Zeiten sind Einzelmessungen** (Python, parallel erzeugt); „LB3 und LB4 sparen keine Zeit“ gilt für diese Umsetzung, die Vorausschau ist nicht optimiert.
- **Eigene Konstruktion;** die Zuordnung der Zählung „kein sicherer Stapel“ zu Zhu u. a. 2012 ist aus dem Gedächtnis und nicht nachgeprüft.
- **Nur restricted, nur volle Buchten, Platz 2 in den Tabellen,** Zufallsbuchten aus der Zufallsfolge von Python.
- **Kleine Zellen** in der Suchtabelle: 5 × 3 mit 60, 4 × 4 mit 60, 5 × 4 mit 40 Buchten.
- **Zwei Lagen:** Für 4, 5 und 6 Stapel sind es Zufallsbuchten (Seeds ab 1000), nicht alle; vollständig ist nur 3 × 2.

## Verifikation

- **Kern:** Zustände von Hand (Abruf, Blocker, Ziel), jede der vier Schranken an Handbuchten (Hand-Bucht, Gegenbeispiel aus Stück 1, der Fehlschlag, eine Bucht, in der erst die Platzgrenze LB3 stärker macht, die Alltags-Bucht für LB4), Knoten- und Stufenzahlen, Reihenfolge der Zielstapel.
- **Orakel:** Optimum gegen eine **eigene Rekursion über alle Platzierungen** (ohne Untergrenze, ohne IDA\*) in allen 120 Buchten 3 × 2; **Zulässigkeit und Dominanz** der Schranken in allen erreichbaren Zuständen dieser Buchten und in Stichproben; LB2 bis LB4 gegen **zweite Umsetzungen durch Ausprobieren aller Platzierungsfolgen** in über 700 Zuständen; LB2 verfehlt genau eine Bucht 3 × 2.
- **Zahlen im README:** jede Zahl der Befunde in `tests/test_claims.py` (gespeicherte Bänder); die Zelle 3 × 2, alle Buchten 3 × 2 und die Knotenzahlen von 3 × 3 werden frisch nachgerechnet, ohne Zeiten.
- **Verdikte:** reine Funktionen, jede Schwelle (90 % „fast vollständig“, Knotenfaktor 1,5, Zeitfaktor 1,0) und jede genannte Zahl an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Inhalt (Kennzahlen je Preset, Tabellenzeilen), Layout, Footer, Laufzeit-Importe, Abbildungen (Farben, gesperrte Achsen, logarithmische Achsen ohne `add_hline`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Aufbau nach DEMO-PLAYBOOK §2) |
| `generate_precomputed.py` | erzeugt `sgu_bands.json` (Stärke, zwei Lagen, Suche) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, plotly |
| `sgu_algorithm.py` | die vier Untergrenzen und die Suche (IDA\* mit Zustandsmerken) |
| `sgu_bands.json` | vorberechnete Kennzahlen der festen Buchten je Zelle |
| `sgu_constants.py` | Regler-Grenzen, Limits, Zellen, Schwellen, Farben, Sonderbuchten, Presets |
| `sgu_evaluation.py` | Analyse einer Bucht, Stichproben, Verdikte (reine Funktionen) |
| `sgu_layout.py` | Fester Kopf (Stylesheet) |
| `sgu_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `sgu_scenario.py` | Buchten (volle Buchten, Zufallsbuchten) |
| `sgu_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Behauptungen, Verdikte, Presets, Abbildungen, AppTest, Layout, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Schranken mit mehr als einem Abrufschritt Vorausschau** und eine optimierte Umsetzung von LB4.
- **Die Quelle der Zählung** (Zhu u. a. 2012) im Volltext; die Zuordnung ist ungeprüft.
- **Eine Zeitmessung in der CI:** Zeiten schwanken.
- **PDF-Export:** nicht vorgesehen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

100 Tests, rund eine Minute.

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
