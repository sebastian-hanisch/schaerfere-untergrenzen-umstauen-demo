"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import sgu_algorithm as A
import sgu_constants as C
import sgu_evaluation as ev


def test_sorted_and_trivial_bays_have_every_bound_zero():
    for bay in (((2, 1), (3,)), ((2,), (1,)), ((1,),), ((3, 2), (1,))):
        st = A.autopop(bay)[0]
        assert not any(st) and A.bound_values(bay, 3) == {k: 0 for k in A.BOUNDS}
        assert A.search(bay, 3, "LB4").optimum == 0


def test_target_on_top_needs_no_extra_term():
    st = ((2, 1), (3, 4))                                                           # die 1 liegt oben, wird abgerufen, dann die 2, dann die 3
    assert A.autopop(st)[0] == ((), (3, 4))
    st, _ = A.autopop(((3, 4), (5, 2, 6), (1,)))                                    # nach dem Abruf der 1 liegt die 6 über der 2
    assert A.blockers_above_target(st) == (2, 1, [6])
    assert A.lb1(st) == 2 and A.lb2(st) == 2                                        # blockiert sind 4 und 6; die 6 hat einen sicheren Stapel (der leere)


def test_no_room_means_no_placement_and_an_infinite_bound():
    bay = ((1, 5), (2, 3))                                                          # beide Stapel voll (Höchsthöhe 2): die 5 kann nirgends hin
    assert A.lb3(bay, 2) == A.INF and A.lb4(bay, 2) == A.INF
    r = A.search(bay, 2, "LB2", cap=50)
    assert r.optimum is None and r.capped and r.nodes == 50                         # kein Optimum, das Knotenlimit bricht die Suche ab


def test_cap_reached_returns_no_optimum():
    r = A.search(((1, 6, 7, 8), (2, 3), (4, 5)), 4, "LB1", cap=3)
    assert r.optimum is None and r.capped and r.nodes == 3
    full = A.search(((1, 6, 7, 8), (2, 3), (4, 5)), 4, "LB1")
    assert full.optimum == 8 and not full.capped


def test_explain_rows_for_the_everyday_and_hand_bays():
    assert ev.explain_rows(C.HAND_BAY, C.HAND_HEIGHT) == ({"target": 1, "blocker": 5, "others": "Stapel 2: 2, Stapel 3: 4", "safe": False},)
    rows = ev.explain_rows(((7, 1, 4), (2, 3, 9), (6, 5, 8)), 5)
    assert rows == ({"target": 1, "blocker": 4, "others": "Stapel 2: 2, Stapel 3: 5", "safe": True},)
    rows = ev.explain_rows(((1, 5, 6), (2,), ()), 4)
    assert [r["blocker"] for r in rows] == [6, 5] and rows[0]["others"] == "Stapel 2: 2, Stapel 3: leer" and all(r["safe"] for r in rows)
    assert ev.explain_rows(((),), 3) == ()


def test_analysis_runs_every_bound_and_the_optima_agree():
    a = ev.analyse(ev.Settings(3, 2, 2, C.MISS_SEED))
    assert a.bay == ((3, 6), (1, 5), (4, 2)) and a.height == 4 and a.containers == 6
    assert a.bounds == {"LB1": 2, "LB2": 3, "LB3": 3, "LB4": 3} and a.optimum == 4
    assert list(a.runs) == list(A.BOUNDS) and all(r.optimum == 4 and not r.capped for r in a.runs.values())


def test_analysis_reports_a_missing_optimum_when_the_reference_search_is_capped(monkeypatch):
    monkeypatch.setattr(C, "REF_CAP", 2)
    a = ev.analyse(ev.Settings(3, 3, 2, 12))
    assert a.optimum is None and a.runs["LB2"].capped
    kind, text = ev.verdict_bay(a)
    assert kind == "info" and "nicht bewiesen" in text and "Knotenlimit 2" in text


def test_number_formats():
    assert ev.num(5) == "5" and ev.num(1234) == "1 234" and ev.num(394444) == "394 444"
    assert ev.num_f(5.0) == "5" and ev.num_f(71.5) == "71,5" and ev.num_f(1234.0) == "1 234" and ev.num_f(0.9999999999999987) == "1"
    assert ev.dec(5.0) == "5" and ev.dec(1.5234) == "1,52" and ev.dec(0.33333) == "0,33" and ev.dec(4.999999999) == "5"
    assert ev.ms_text(0.25) == "0,2" and ev.ms_text(12.4) == "12" and ev.ms_text(9.96) == "10,0"
    assert ev.sec_text(0.03) == "0,03" and ev.sec_text(9.994) == "9,99" and ev.sec_text(10.04) == "10,0"
    assert ev.time_text(0.4) == "0,4 ms" and ev.time_text(31.6) == "32 ms" and ev.time_text(1500) == "1,50 s" and ev.time_text(29700) == "29,7 s"
    assert ev.ratio_text(1.7142) == "1,7" and ev.ratio_text(0.75) == "0,8" and ev.ratio_text(12.4) == "12"
    assert ev.percent_text(0.0259) == "2,6 %" and ev.percent_text(0.92) == "92 %"


def test_cell_stats_and_search_stats_on_given_rows():
    rows = [{"seed": 0, "opt": 4, "LB1": 3, "LB2": 4, "LB3": 4, "LB4": 4}, {"seed": 1, "opt": 6, "LB1": 4, "LB2": 5, "LB3": 5, "LB4": 6}]
    st = ev.cell_stats(rows)
    assert st["n"] == 2 and st["opt_mean"] == 5 and st["hit"] == {"LB1": 0, "LB2": 1, "LB3": 1, "LB4": 2}
    assert st["gap_mean"] == {"LB1": 1.5, "LB2": 0.5, "LB3": 0.5, "LB4": 0.0} and st["gap_max"] == {"LB1": 2, "LB2": 1, "LB3": 1, "LB4": 0} and sum(st["violations"].values()) == 0
    bad = ev.cell_stats([{"seed": 0, "opt": 3, "LB1": 3, "LB2": 4, "LB3": 4, "LB4": 4}])
    assert bad["violations"]["LB2"] == 1 and bad["violations"]["LB1"] == 0                  # eine Schranke über dem Optimum würde auffallen
    def row(seed, opt, spec):
        return {"seed": seed, "opt": opt, **{k: {"nodes": n, "ms": ms, "capped": False} for k, (n, ms) in zip(A.BOUNDS, spec)}}

    srows = [row(0, 4, ((10, 1.0), (6, 0.5), (5, 2.0), (4, 4.0))), row(1, 5, ((30, 3.0), (14, 1.5), (9, 5.0), (6, 8.0)))]
    ss = ev.search_stats(srows)
    assert ss["nodes"]["LB1"] == {"median": 20.0, "max": 30} and ss["ms"]["LB2"] == 1.0 and ss["seconds"]["LB4"] == pytest.approx(0.012) and ss["capped"]["LB1"] == 0
    capped = [{"seed": 0, "opt": None, **{k: {"nodes": 100, "ms": 1.0, "capped": k == "LB1"} for k in A.BOUNDS}}, {"seed": 1, "opt": 3, **{k: {"nodes": 7, "ms": 2.0, "capped": False} for k in A.BOUNDS}}]
    sc = ev.search_stats(capped)
    assert sc["capped"]["LB1"] == 1 and sc["nodes"]["LB1"]["median"] == 7 and sc["nodes"]["LB2"]["median"] == 53.5
