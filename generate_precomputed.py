"""Erzeugt sgu_bands.json: Kennzahlen der festen Buchten (Seeds ab 0, Platz 2) für drei Auswertungen.

    python generate_precomputed.py

"zellen":     je Zelle (HIT_CELLS) die vier Schranken gegen das Optimum: Treffer, Lücke (Mittel, Maximum), Verletzungen (Schranke über dem Optimum).
"suche":      je Zelle (SEARCH_CELLS) die Suche mit jeder Schranke: Knoten (Median, Maximum), Zeit (Median je Bucht, Summe), Läufe am Limit.
"zwei_lagen": je Zelle mit zwei Lagen (TWO_LAYER_CELLS, Seeds ab TWO_LAYER_SEED0) und alle 120 Buchten 3 x 2 ("alle32") die Zahl der Buchten, in denen die Schranke das Optimum verfehlt.

Rechenzeit einige Minuten (die Suche mit LB4 in 5 x 4 ist die langsamste Zelle; die Zellen laufen in getrennten Prozessen, die Zeiten sind deshalb Einzelmessungen unter Last und
schwanken). Dieselben Funktionen wie die Tests (`sgu_evaluation.cell_rows`, `cell_stats`, `search_rows`, `search_stats`, `miss_stats`); die Datei speichert nur Kennzahlen, keine Zeilen."""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import sgu_constants as C
import sgu_evaluation as ev

sys.stdout.reconfigure(encoding="utf-8")


def job(kind, stacks, layers, n):
    if kind == "zellen":
        return kind, ev.cell_key(stacks, layers), ev.cell_stats(ev.cell_rows(stacks, layers, C.DEFAULT_EXTRA, range(n)))
    if kind == "suche":
        return kind, ev.cell_key(stacks, layers), ev.search_stats(ev.search_rows(stacks, layers, C.DEFAULT_EXTRA, range(n)))
    if kind == "alle32":
        return "zwei_lagen", "alle32", ev.miss_stats(ev.all_3x2_bays(), 4)
    return "zwei_lagen", ev.cell_key(stacks, layers), ev.miss_stats(ev.two_layer_bays(stacks, n), layers + C.DEFAULT_EXTRA)


def main():
    tasks = [("suche", s, l, n) for s, l, n in reversed(C.SEARCH_CELLS)]               # die langsamen zuerst
    tasks += [("zwei", s, 2, n) for s, _, n in C.TWO_LAYER_CELLS] + [("alle32", 3, 2, 0)]
    tasks += [("zellen", s, l, n) for s, l, n in C.HIT_CELLS]
    out = {"zellen": {}, "suche": {}, "zwei_lagen": {}}
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 2)) as pool:
        futures = {pool.submit(job, *t): t for t in tasks}
        for fut in as_completed(futures):
            kind, key, stats = fut.result()
            out[kind][key] = stats
            print(kind, key, "fertig", flush=True)
    with open("sgu_bands.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("geschrieben: sgu_bands.json", flush=True)


if __name__ == "__main__":
    main()
