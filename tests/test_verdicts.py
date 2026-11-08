"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import sgu_algorithm as A
import sgu_constants as C
import sgu_evaluation as ev


def _run(opt=5, nodes=11, ms=0.2, capped=False):
    return ev.Run(None if capped else opt, nodes, ms, capped)


def _a(b1=4, b2=4, b3=4, b4=5, opt=5, runs=None, capped_ref=False):
    runs = runs or {k: _run(opt) for k in A.BOUNDS}
    if capped_ref:
        runs = {**runs, "LB2": ev.Run(None, 300000, 900.0, True)}
    return ev.Analysis(((1,),), 5, 9, {"LB1": b1, "LB2": b2, "LB3": b3, "LB4": b4}, runs, ())


def test_bay_verdict_three_states_and_numbers():
    kind, text = ev.verdict_bay(_a())
    assert kind == "success" and text == "Die erste Schranke, die das Optimum 5 trifft, ist LB4 (LB1 4, LB2 4, LB3 4, LB4 5); die Zählung aus Stück 2 liegt um 1 unter dem Optimum."
    kind, text = ev.verdict_bay(_a(3, 4, 4, 4, opt=4))
    assert kind == "success" and text.startswith("Die erste Schranke, die das Optimum 4 trifft, ist LB2 (LB1 3, LB2 4") and "liegt um 1 unter" in text
    kind, text = ev.verdict_bay(_a(5, 5, 5, 5, opt=5))
    assert kind == "info" and text == "Schon die einfache Zählung trifft das Optimum 5 (LB1 5, LB2 5, LB3 5, LB4 5); eine schärfere Schranke wird nicht gebraucht."
    kind, text = ev.verdict_bay(_a(5, 5, 5, 5, opt=6))
    assert kind == "warning" and text == ("Keine der vier Schranken trifft das Optimum 6 (LB1 5, LB2 5, LB3 5, LB4 5): auch LB1 liegt um 1 unter dem Optimum. "
                                          "Die Lücke kommt aus späteren Abrufschritten.")
    kind, text = ev.verdict_bay(_a(4, 6, 6, 7, opt=9))
    assert kind == "warning" and "auch LB4 liegt um 2 unter" in text                       # die größte Schranke wird genannt


def test_bay_verdict_without_a_proven_optimum():
    kind, text = ev.verdict_bay(_a(capped_ref=True))
    assert kind == "info" and text == "Das Optimum ist nicht bewiesen (Knotenlimit 300 000 der Suche mit LB2). Die Schranken: LB1 4, LB2 4, LB3 4, LB4 5; größter Wert 5."


def test_result_rows_by_hand():
    runs = {"LB1": _run(5, 11, 0.2), "LB2": _run(5, 9, 0.6), "LB3": _run(5, 9, 0.5), "LB4": _run(5, 6, 1500.0)}
    rows = ev.result_rows(_a(runs=runs))
    assert [r["value"] for r in rows] == ["4", "4", "4", "5"] and [r["gap"] for r in rows] == ["1", "1", "1", "0"]
    assert rows[0] == {"name": "LB1: Blocker zählen (Stück 2)", "value": "4", "gap": "1", "effort": "11 Knoten, 0,2 ms"}
    assert rows[3]["effort"] == "6 Knoten, 1,50 s" and rows[3]["name"] == "LB4: ein Abrufschritt voraus"
    runs["LB3"] = _run(capped=True, nodes=40000)
    capped_rows = ev.result_rows(_a(runs=runs))
    assert capped_rows[2]["effort"] == "über dem Limit (40 000 Knoten)"
    ref = ev.result_rows(_a(capped_ref=True))
    assert ref[1]["effort"] == "über dem Limit (300 000 Knoten)" and ref[0]["gap"] == "–"


def _hits(n=100, hit=(19, 57, 59, 73), gap=(1.52, 0.64, 0.61, 0.34)):
    return {"n": n, "opt_mean": 5.05, "hit": dict(zip(A.BOUNDS, hit)), "gap_mean": dict(zip(A.BOUNDS, gap)), "gap_max": dict(zip(A.BOUNDS, (4, 3, 3, 2))), "violations": {k: 0 for k in A.BOUNDS}}


def test_hits_verdict_three_states_and_numbers():
    kind, text = ev.verdict_hits(_hits(), "3 × 3")
    assert kind == "info" and text == ("3 × 3: Das Optimum treffen LB1 in 19 von 100 Buchten, LB2 in 57, LB3 in 59, LB4 in 73; mittlere Lücke 1,52 (LB1), 0,64 (LB2), 0,34 (LB4). "
                                       "Die Zählung der Blocker ohne sicheren Stapel schließt einen Teil der Lücke.")
    kind, text = ev.verdict_hits(_hits(hit=(67, 90, 90, 90), gap=(0.33, 0.1, 0.1, 0.1)), "3 × 2")
    assert kind == "success" and text.endswith("schließt die Lücke fast vollständig.")           # genau 90 von 100 zählt als „fast vollständig“
    assert ev.verdict_hits(_hits(hit=(67, 89, 89, 89)), "x")[0] == "info" and C.HIT_SHARE_ALMOST == 0.9
    kind, text = ev.verdict_hits(_hits(hit=(30, 30, 30, 40)), "x")
    assert kind == "warning" and text.endswith("LB2 bringt hier gegenüber LB1 nichts.")
    assert ev.verdict_hits(_hits(hit=(30, 20, 30, 40)), "x")[0] == "warning"                     # LB2 nie schlechter als LB1; trotzdem „bringt nichts“, wenn nicht mehr Treffer


def _search(n=100, nodes=((16, 123), (8, 70), (8, 45), (6, 36)), ms=(0.3, 0.2, 0.4, 0.5)):
    return {"n": n, "nodes": {k: {"median": float(a), "max": b} for k, (a, b) in zip(A.BOUNDS, nodes)}, "ms": dict(zip(A.BOUNDS, ms)), "seconds": {k: 0.1 for k in A.BOUNDS}, "capped": {k: 0 for k in A.BOUNDS}}


def test_search_verdict_three_states_and_numbers():
    kind, text = ev.verdict_search(_search(), "3 × 3")
    assert kind == "success" and text == ("3 × 3: Gegenüber LB1 sinkt im Median die Knotenzahl mit LB2 um den Faktor 2,0 und mit LB4 um den Faktor 2,7; "
                                          "die Zeit liegt mit LB2 beim 0,7-Fachen und mit LB4 beim 1,7-Fachen von LB1. LB2 spart Knoten und Zeit; LB4 spart Knoten, kostet aber mehr Zeit.")
    kind, text = ev.verdict_search(_search(ms=(0.3, 0.3, 0.4, 0.2)), "x")                      # Zeitverhältnis genau 1,0: zählt noch als „nicht langsamer“
    assert kind == "success" and text.endswith("Beide sparen Knoten und Zeit.")
    kind, text = ev.verdict_search(_search(ms=(0.3, 0.31, 0.4, 0.5)), "x")
    assert kind == "info" and text.endswith("LB2 spart Knoten, aber keine Zeit.")
    kind, text = ev.verdict_search(_search(nodes=((15, 100), (11, 80), (10, 70), (9, 60))), "x")        # 15 / 11 = 1,36 < 1,5
    assert kind == "warning" and text.endswith("Die schärferen Schranken sparen hier kaum Knoten.")
    assert ev.verdict_search(_search(nodes=((15, 100), (10, 80), (10, 70), (9, 60))), "x")[0] == "success"  # genau 1,5 zählt
    assert C.NODE_GAIN == 1.5 and C.TIME_FACTOR == 1.0


def test_two_layer_verdict_two_states_and_numbers():
    kind, text = ev.verdict_two({"n": 1500, "miss": {"LB1": 489, "LB2": 0, "LB3": 0, "LB4": 0}}, "4 × 2")
    assert kind == "success" and text == "4 × 2: LB1 verfehlt das Optimum in 489 von 1500 Buchten, LB2 in 0. In dieser Stichprobe trifft die zweite Zählung bei zwei Lagen das Optimum in allen Buchten; erschöpfend gerechnet gibt es vereinzelte Ausnahmen."
    kind, text = ev.verdict_two({"n": 120, "miss": {"LB1": 44, "LB2": 1, "LB3": 1, "LB4": 1}}, "3 × 2")
    assert kind == "info" and text == ("3 × 2: LB1 verfehlt das Optimum in 44 von 120 Buchten, LB2 in 1. "
                                       "Bei zwei Lagen trifft die zweite Zählung das Optimum bis auf wenige Ausnahmen.")
