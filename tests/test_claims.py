"""Aussagen der Demo und des READMEs gegen die vorberechneten Bänder und gegen eine frische Nachrechnung kleiner Zellen (DEMO-PLAYBOOK §5, §12).

Zeiten werden nicht frisch verglichen (sie schwanken); Knotenzahlen und Treffer sind deterministisch und müssen bei der Nachrechnung gleich sein."""

import sgu_algorithm as A
import sgu_constants as C
import sgu_evaluation as ev


def K(s, l):
    return ev.cell_key(s, l)


def _bands():
    return ev.load_bands()


def test_the_stored_cells_cover_exactly_the_cells_of_the_constants():
    b = _bands()
    assert {k: v["n"] for k, v in b["zellen"].items()} == {K(s, l): n for s, l, n in C.HIT_CELLS}
    assert {k: v["n"] for k, v in b["suche"].items()} == {K(s, l): n for s, l, n in C.SEARCH_CELLS}
    assert set(b["zwei_lagen"]) == {"alle32", K(4, 2), K(5, 2), K(6, 2)}
    assert {K(s, 2): n for s, _, n in C.TWO_LAYER_CELLS} == {k: v["n"] for k, v in b["zwei_lagen"].items() if k != "alle32"}


def test_no_bound_is_ever_above_the_optimum_and_the_order_of_the_bounds_holds():
    for c in _bands()["zellen"].values():
        assert all(v == 0 for v in c["violations"].values())
        h, g = c["hit"], c["gap_mean"]
        assert h["LB1"] <= h["LB2"] <= h["LB3"] <= h["LB4"] <= c["n"] and g["LB1"] >= g["LB2"] >= g["LB3"] >= g["LB4"] >= 0


def test_two_layers_lb2_misses_exactly_one_of_2020_bays():
    z = _bands()["zwei_lagen"]
    assert sum(c["n"] for c in z.values()) == 2020 and sum(c["miss"]["LB2"] for c in z.values()) == 1
    assert z["alle32"]["miss"] == {"LB1": 44, "LB2": 1, "LB3": 1, "LB4": 1} and z["alle32"]["lb2_miss"] == [[[1, 5], [3, 6], [4, 2]]]
    assert [z[K(s, 2)]["miss"]["LB1"] for s in (4, 5, 6)] == [489, 86, 26] and all(z[K(s, 2)]["miss"]["LB2"] == 0 for s in (4, 5, 6))


def test_the_hit_numbers_the_readme_quotes():
    z = _bands()["zellen"]
    assert [z[K(3, 3)]["hit"][k] for k in A.BOUNDS] == [19, 57, 59, 73] and [z[K(4, 3)]["hit"][k] for k in A.BOUNDS] == [20, 63, 66, 80]
    assert [z[K(4, 4)]["hit"][k] for k in A.BOUNDS] == [4, 24, 24, 37] and [z[K(5, 4)]["hit"][k] for k in A.BOUNDS] == [3, 19, 19, 28]
    assert [z[K(s, 2)]["hit"]["LB2"] for s in (3, 4)] == [100, 100] and [z[K(s, 2)]["hit"]["LB1"] for s in (3, 4)] == [67, 70]
    assert round(z[K(3, 4)]["gap_mean"]["LB1"], 2) == 3.24 and round(z[K(3, 4)]["gap_mean"]["LB2"], 2) == 1.83 and round(z[K(5, 3)]["gap_mean"]["LB4"], 2) == 0.26


def test_the_search_numbers_the_readme_quotes():
    s = _bands()["suche"]
    assert all(c["capped"] == {k: 0 for k in A.BOUNDS} for c in s.values())
    assert [s[K(5, 4)]["nodes"][k]["median"] for k in A.BOUNDS] == [284.0, 134.5, 120.5, 56.0]
    assert [s[K(5, 4)]["nodes"][k]["max"] for k in A.BOUNDS] == [56710, 28017, 26641, 11239]
    assert [s[K(4, 4)]["nodes"][k]["median"] for k in A.BOUNDS] == [173.5, 84.0, 70.0, 43.0] and s[K(3, 3)]["nodes"]["LB2"]["max"] == 70
    for c in s.values():          # LB2 spart Knoten in jeder Zelle; ihre Zeit liegt in keiner Zelle über der von LB1 (gespeicherte Einzelmessungen)
        assert c["nodes"]["LB2"]["median"] < c["nodes"]["LB1"]["median"] and c["ms"]["LB2"] <= c["ms"]["LB1"]
    for key in (K(4, 4), K(5, 4)):  # bei den großen Zellen kostet die Vorausschau mehr Zeit, als sie an Knoten spart
        assert s[key]["ms"]["LB4"] > s[key]["ms"]["LB1"] and s[key]["seconds"]["LB4"] > s[key]["seconds"]["LB1"]
        assert s[key]["nodes"]["LB4"]["median"] < s[key]["nodes"]["LB1"]["median"]


def test_a_fresh_recomputation_of_the_3_by_2_cell_reproduces_the_stored_band():
    stored = _bands()["zellen"][K(3, 2)]
    fresh = ev.cell_stats(ev.cell_rows(3, 2, C.DEFAULT_EXTRA, range(100)))
    assert fresh == stored


def test_a_fresh_recomputation_of_all_bays_3x2_reproduces_the_stored_misses():
    assert ev.miss_stats(ev.all_3x2_bays(), 4) == _bands()["zwei_lagen"]["alle32"]


def test_a_fresh_recomputation_of_the_node_counts_of_3x3_reproduces_the_stored_band():
    stored = _bands()["suche"][K(3, 3)]
    fresh = ev.search_stats(ev.search_rows(3, 3, C.DEFAULT_EXTRA, range(100)))
    assert fresh["nodes"] == stored["nodes"] and fresh["capped"] == stored["capped"] and fresh["n"] == stored["n"]
