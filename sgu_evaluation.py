"""Kennzahlen, Verdikt-Logik, vorberechnete Tabellen. Reine Funktionen: die App ruft st.<Art>(Text), die Tests prüfen jede Zahl und jede Schwelle."""

import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

import sgu_algorithm as A
import sgu_constants as C
from sgu_scenario import make_bay, max_height

BANDS_FILE = Path(__file__).resolve().parent / "sgu_bands.json"
BOUND_NAMES = {
    "LB1": "LB1: Blocker zählen (Stück 2)",
    "LB2": "LB2: plus Blocker ohne sicheren Stapel",
    "LB3": "LB3: plus beste Platzierung der Blocker",
    "LB4": "LB4: ein Abrufschritt voraus",
}


@dataclass(frozen=True)
class Settings:
    stacks: int = C.DEFAULT_STACKS
    layers: int = C.DEFAULT_LAYERS
    extra: int = C.DEFAULT_EXTRA
    seed: int = C.EVERYDAY_SEED


@dataclass(frozen=True)
class Run:
    optimum: int | None     # None bei Knotenlimit
    nodes: int
    ms: float
    capped: bool


@dataclass(frozen=True)
class Analysis:
    bay: tuple
    height: int
    containers: int
    bounds: dict            # {"LB1": Wert, ...} an der Wurzel (nach dem ersten Abruf)
    runs: dict              # {"LB1": Run, ...}: die Suche mit der jeweiligen Untergrenze
    rows: tuple             # Blocker über dem ersten Ziel (Erklärung von Hand), siehe explain_rows

    @property
    def optimum(self):
        """Optimum aus der Suche mit LB2 (Bezugswert, Limit REF_CAP); None, wenn nicht bewiesen."""
        return self.runs["LB2"].optimum


def _timed_search(bay, height, bound, cap) -> Run:
    t0 = time.perf_counter()
    r = A.search(bay, height, bound, cap)
    return Run(r.optimum, r.nodes, (time.perf_counter() - t0) * 1000.0, r.capped)


def explain_rows(bay, height) -> tuple:
    """Zu jedem Container über dem ersten Ziel: die früheste Abrufnummer der anderen Stapel und ob es einen sicheren Stapel gibt (einen mit späterem Minimum)."""
    st, _ = A.autopop(bay)
    if not any(st):
        return ()
    t, i, blk = A.blockers_above_target(st)
    others = [(k, A.stack_min(s)) for k, s in enumerate(st) if k != i]
    top = max((m for _, m in others), default=-1)
    text = ", ".join(f"Stapel {k + 1}: " + ("leer" if m == A.INF else str(m)) for k, m in others)
    return tuple({"target": t, "blocker": c, "others": text, "safe": c < top} for c in blk)


def analyse(settings: Settings) -> Analysis:
    bay = make_bay(settings.stacks, settings.layers, settings.seed)
    height = max_height(settings.layers, settings.extra)
    runs = {"LB2": _timed_search(bay, height, "LB2", C.REF_CAP)}
    for name in A.BOUNDS:
        if name != "LB2":
            runs[name] = _timed_search(bay, height, name, C.LIVE_CAP)
    runs = {name: runs[name] for name in A.BOUNDS}
    opts = {r.optimum for r in runs.values() if r.optimum is not None}
    if len(opts) > 1:
        raise AssertionError(f"Suchläufe mit verschiedenen Untergrenzen widersprechen sich: {opts}")
    return Analysis(bay, height, settings.stacks * settings.layers, A.bound_values(bay, height), runs, explain_rows(bay, height))


# ---------------------------------------------------------------- Formate

def num(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def num_f(x: float) -> str:
    """Zahl mit Leerzeichen als Tausendertrenner; hat sie einen Nachkommaanteil (Median einer geraden Zahl von Läufen), mit einer Nachkommastelle und Komma."""
    x = round(float(x), 6)
    if x.is_integer():
        return num(int(x))
    whole, frac = f"{x:.1f}".split(".")
    return f"{num(int(whole))},{frac}"


def dec(x: float, digits: int = 2) -> str:
    """Dezimalzahl mit Komma; ganzzahlige Werte ohne Nachkommastellen."""
    x = round(float(x), 6)
    return num(int(x)) if x.is_integer() else f"{x:.{digits}f}".replace(".", ",")


def ms_text(ms: float) -> str:
    """Millisekunden: unter 10 mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    return f"{ms:.1f}".replace(".", ",") if ms < 10 else num(round(ms))


def sec_text(s: float) -> str:
    """Sekunden: unter 10 mit zwei, sonst mit einer Nachkommastelle (Komma)."""
    return (f"{s:.2f}" if s < 10 else f"{s:.1f}").replace(".", ",")


def time_text(ms: float) -> str:
    """Zeit mit Einheit: unter 1000 ms in Millisekunden, sonst in Sekunden."""
    return f"{ms_text(ms)} ms" if ms < 1000 else f"{sec_text(ms / 1000)} s"


def ratio_text(x: float) -> str:
    """Verhältnis: unter 10 mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    return f"{x:.1f}".replace(".", ",") if x < 10 else num(round(x))


def percent_text(x: float) -> str:
    """Anteil als Prozent: unter 10 % mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    p = x * 100
    return (f"{p:.1f}" if p < 10 else f"{p:.0f}").replace(".", ",") + " %"


# ---------------------------------------------------------------- Verdikt einer Bucht

def verdict_bay(a: Analysis) -> tuple[str, str]:
    """Verdikt der Kernfrage: welche Schranke trifft das Optimum zuerst?"""
    b = a.bounds
    vals = ", ".join(f"{k} {b[k]}" for k in A.BOUNDS)
    opt = a.optimum
    if opt is None:
        return "info", f"Das Optimum ist nicht bewiesen (Knotenlimit {num(C.REF_CAP)} der Suche mit LB2). Die Schranken: {vals}; größter Wert {max(b.values())}."
    first = next((k for k in A.BOUNDS if b[k] == opt), None)
    if first == "LB1":
        return "info", f"Schon die einfache Zählung trifft das Optimum {opt} ({vals}); eine schärfere Schranke wird nicht gebraucht."
    if first is not None:
        return "success", f"Die erste Schranke, die das Optimum {opt} trifft, ist {first} ({vals}); die Zählung aus Stück 2 liegt um {opt - b['LB1']} unter dem Optimum."
    best = max(b, key=lambda k: b[k])
    return "warning", f"Keine der vier Schranken trifft das Optimum {opt} ({vals}): auch {best} liegt um {opt - b[best]} unter dem Optimum. Die Lücke kommt aus späteren Abrufschritten."


def result_rows(a: Analysis) -> list[dict]:
    """Zeilen der Ergebnistabelle: je Schranke Wert, Lücke zum Optimum, Aufwand der Suche mit dieser Schranke."""
    rows = []
    for k in A.BOUNDS:
        r = a.runs[k]
        gap = "–" if a.optimum is None else str(a.optimum - a.bounds[k])
        effort = f"über dem Limit ({num(C.LIVE_CAP if k != 'LB2' else C.REF_CAP)} Knoten)" if r.capped else f"{num(r.nodes)} Knoten, {time_text(r.ms)}"
        rows.append({"name": BOUND_NAMES[k], "value": str(a.bounds[k]), "gap": gap, "effort": effort})
    return rows


# ---------------------------------------------------------------- Stichproben (vorberechnet)

def _stat(xs):
    xs = list(xs)
    return {"median": float(median(xs)), "max": max(xs)}


def cell_rows(stacks: int, layers: int, extra: int, seeds, cap: int = C.REF_CAP) -> list[dict]:
    """Je Bucht: Optimum (Suche mit LB2) und die vier Schranken an der Wurzel. Buchten ohne bewiesenes Optimum fehlen."""
    height = max_height(layers, extra)
    out = []
    for sd in seeds:
        bay = make_bay(stacks, layers, sd)
        r = A.search(bay, height, "LB2", cap)
        if r.optimum is None:
            continue
        out.append({"seed": sd, "opt": r.optimum, **A.bound_values(bay, height)})
    return out


def cell_stats(rows: list[dict]) -> dict:
    """Je Zelle: Zahl der Buchten, mittleres Optimum, je Schranke Treffer (gleich dem Optimum), Lücke (Mittel, Maximum), Verletzungen (Schranke über dem Optimum)."""
    gaps = {k: [r["opt"] - r[k] for r in rows] for k in A.BOUNDS}
    return {"n": len(rows), "opt_mean": mean(r["opt"] for r in rows),
            "hit": {k: sum(1 for g in gaps[k] if g == 0) for k in A.BOUNDS},
            "gap_mean": {k: mean(gaps[k]) for k in A.BOUNDS}, "gap_max": {k: max(gaps[k]) for k in A.BOUNDS},
            "violations": {k: sum(1 for g in gaps[k] if g < 0) for k in A.BOUNDS}}


def search_rows(stacks: int, layers: int, extra: int, seeds, cap: int = 1_000_000) -> list[dict]:
    """Je Bucht und Schranke: Knoten und Zeit der Suche; die Optima aller fertigen Läufe müssen gleich sein."""
    height = max_height(layers, extra)
    out = []
    for sd in seeds:
        bay = make_bay(stacks, layers, sd)
        row = {"seed": sd}
        opts = set()
        for k in A.BOUNDS:
            run = _timed_search(bay, height, k, cap)
            row[k] = {"nodes": run.nodes, "ms": run.ms, "capped": run.capped}
            if run.optimum is not None:
                opts.add(run.optimum)
        if len(opts) > 1:
            raise AssertionError(f"Bucht {sd}: Suchläufe mit verschiedenen Untergrenzen widersprechen sich: {opts}")
        row["opt"] = next(iter(opts), None)
        out.append(row)
    return out


def search_stats(rows: list[dict]) -> dict:
    """Je Zelle und Schranke: Knoten (Median, Maximum) der fertigen Läufe, Zeit (Median, Summe), Zahl der Läufe am Limit."""
    out = {"n": len(rows), "nodes": {}, "ms": {}, "seconds": {}, "capped": {}}
    for k in A.BOUNDS:
        done = [r[k] for r in rows if not r[k]["capped"]]
        out["nodes"][k] = _stat(x["nodes"] for x in done)
        out["ms"][k] = float(median(x["ms"] for x in done))
        out["seconds"][k] = sum(r[k]["ms"] for r in rows) / 1000.0
        out["capped"][k] = sum(1 for r in rows if r[k]["capped"])
    return out


def all_3x2_bays() -> list:
    """Alle Buchten 3 x 2 (Nummern 1 bis 6) bis auf Vertauschen der Stapel: 120."""
    seen = set()
    for perm in itertools.permutations(range(1, 7)):
        bay = tuple(tuple(perm[i * 2:(i + 1) * 2]) for i in range(3))
        seen.add(tuple(sorted(bay)))
    return sorted(seen)


def miss_stats(bays, height: int, cap: int = 3_000_000) -> dict:
    """Zahl der Buchten, in denen die Schranke das Optimum verfehlt (Suche mit LB3 als Bezug); dazu die verfehlenden Buchten von LB2."""
    miss = {k: 0 for k in A.BOUNDS}
    lb2_miss = []
    n = 0
    for bay in bays:
        r = A.search(bay, height, "LB3", cap)
        if r.optimum is None:
            continue
        n += 1
        vals = A.bound_values(bay, height)
        for k in A.BOUNDS:
            if vals[k] != r.optimum:
                miss[k] += 1
        if vals["LB2"] != r.optimum:
            lb2_miss.append([list(s) for s in bay])
    return {"n": n, "miss": miss, "lb2_miss": lb2_miss}


def two_layer_bays(stacks: int, count: int) -> list:
    return [make_bay(stacks, 2, C.TWO_LAYER_SEED0 + i) for i in range(count)]


def load_bands() -> dict:
    """Vorberechnete Kennzahlen, erzeugt von generate_precomputed.py: {"zellen": {"s,l": cell_stats}, "suche": {"s,l": search_stats}, "zwei_lagen": {"alle32" oder "s,2": miss_stats}}."""
    return json.loads(BANDS_FILE.read_text(encoding="utf-8"))


def cell_key(stacks: int, layers: int) -> str:
    return f"{stacks},{layers}"


# ---------------------------------------------------------------- Verdikte der Tabellen

def verdict_hits(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt „wie oft trifft die Schranke das Optimum?“ (LB2 gegen LB1, LB4 als Zusatz)."""
    n, hit = stats["n"], stats["hit"]
    text = (f"{name}: Das Optimum treffen LB1 in {hit['LB1']} von {n} Buchten, LB2 in {hit['LB2']}, LB3 in {hit['LB3']}, LB4 in {hit['LB4']}; "
            f"mittlere Lücke {dec(stats['gap_mean']['LB1'])} (LB1), {dec(stats['gap_mean']['LB2'])} (LB2), {dec(stats['gap_mean']['LB4'])} (LB4).")
    if hit["LB2"] >= C.HIT_SHARE_ALMOST * n:
        return "success", text + " Die Zählung der Blocker ohne sicheren Stapel schließt die Lücke fast vollständig."
    if hit["LB2"] > hit["LB1"]:
        return "info", text + " Die Zählung der Blocker ohne sicheren Stapel schließt einen Teil der Lücke."
    return "warning", text + " LB2 bringt hier gegenüber LB1 nichts."


def verdict_search(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt „was hat die Suche von der Schranke?“: Knoten und Zeit von LB2 und LB4 gegen LB1."""
    nodes, ms = stats["nodes"], stats["ms"]
    node2 = nodes["LB1"]["median"] / nodes["LB2"]["median"]
    node4 = nodes["LB1"]["median"] / nodes["LB4"]["median"]
    time2 = ms["LB2"] / ms["LB1"]
    time4 = ms["LB4"] / ms["LB1"]
    text = (f"{name}: Gegenüber LB1 sinkt im Median die Knotenzahl mit LB2 um den Faktor {ratio_text(node2)} und mit LB4 um den Faktor {ratio_text(node4)}; "
            f"die Zeit liegt mit LB2 beim {ratio_text(time2)}-Fachen und mit LB4 beim {ratio_text(time4)}-Fachen von LB1.")
    if node2 >= C.NODE_GAIN and time2 <= C.TIME_FACTOR:
        return "success", text + " LB2 spart Knoten und Zeit; LB4 spart Knoten, kostet aber mehr Zeit." if time4 > C.TIME_FACTOR else text + " Beide sparen Knoten und Zeit."
    if node2 >= C.NODE_GAIN:
        return "info", text + " LB2 spart Knoten, aber keine Zeit."
    return "warning", text + " Die schärferen Schranken sparen hier kaum Knoten."


def verdict_two(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt „zwei Lagen“: wie oft verfehlt LB2 das Optimum?"""
    n, miss = stats["n"], stats["miss"]
    text = f"{name}: LB1 verfehlt das Optimum in {miss['LB1']} von {n} Buchten, LB2 in {miss['LB2']}."
    if miss["LB2"] == 0:
        return "success", text + " In dieser Stichprobe trifft die zweite Zählung bei zwei Lagen das Optimum in allen Buchten; erschöpfend gerechnet gibt es vereinzelte Ausnahmen."
    return "info", text + " Bei zwei Lagen trifft die zweite Zählung das Optimum bis auf wenige Ausnahmen."
