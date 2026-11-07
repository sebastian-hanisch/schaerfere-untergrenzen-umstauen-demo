"""Presets: jede Sonderbucht hat die Eigenschaft, für die sie steht (DEMO-PLAYBOOK §12), und die Hilfetexte nennen nur gemessene Zahlen."""

import pytest

import sgu_constants as C
import sgu_evaluation as ev
import sgu_presets as P


def _analyse(name):
    p = C.PRESETS[name]
    return ev.analyse(ev.Settings(p["stacks"], p["layers"], p["extra"], p["seed"]))


def test_every_preset_is_inside_the_slider_bounds_and_has_help():
    for name, p in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= p[key] <= hi, (name, key)
    assert set(C.PRESET_HELP) == set(C.PRESETS) and all(C.PRESET_HELP.values())


def test_everyday_bay_needs_the_lookahead():
    a = _analyse("Alltag (3 Stapel, 3 Lagen)")
    assert a.bay == ((7, 1, 4), (2, 3, 9), (6, 5, 8)) and a.bounds == {"LB1": 4, "LB2": 4, "LB3": 4, "LB4": 5} and a.optimum == 5
    assert ev.verdict_bay(a)[0] == "success" and "LB4" in ev.verdict_bay(a)[1]


def test_two_layer_bay_is_solved_by_lb2():
    a = _analyse("Zwei Lagen: LB2 reicht (4 Stapel, 2 Lagen)")
    assert a.bay == ((1, 6), (8, 3), (2, 7), (5, 4)) and a.bounds["LB1"] == 2 and a.bounds["LB2"] == a.optimum == 3


def test_big_gain_bay_closes_three_hubs_with_lb2():
    a = _analyse("LB2 schließt die Lücke (4 Stapel, 4 Lagen)")
    assert a.bounds == {"LB1": 7, "LB2": 10, "LB3": 10, "LB4": 10} and a.optimum == 10 and a.containers == 16


def test_gap_bay_leaves_a_gap_for_every_bound():
    a = _analyse("Die Lücke bleibt (3 Stapel, 3 Lagen)")
    assert set(a.bounds.values()) == {5} and a.optimum == 6 and ev.verdict_bay(a)[0] == "warning"


def test_miss_bay_is_the_one_where_lb2_fails():
    a = _analyse("LB2 verfehlt (3 Stapel, 2 Lagen)")
    assert a.bay == ((3, 6), (1, 5), (4, 2)) and sorted(a.bay) == sorted(((1, 5), (3, 6), (4, 2))) and a.bounds == {"LB1": 2, "LB2": 3, "LB3": 3, "LB4": 3} and a.optimum == 4


def test_cost_bay_shows_more_time_for_fewer_nodes():
    a = _analyse("Schärfer lohnt nicht (5 Stapel, 4 Lagen)")
    assert a.bounds == {"LB1": 14, "LB2": 16, "LB3": 16, "LB4": 16} and a.optimum == 18 and a.containers == 20
    nodes = {k: r.nodes for k, r in a.runs.items()}
    assert nodes["LB4"] < nodes["LB2"] < nodes["LB1"] and not any(r.capped for r in a.runs.values())       # Zeiten schwanken: nur die Knotenzahlen werden geprüft


def test_the_default_settings_are_the_everyday_preset():
    assert {s: P.SETTING_SPECS[s].default for s in P.SETTING_SPECS} == {"stacks_slider": 3, "layers_slider": 3, "extra_slider": 2, "seed_input": C.EVERYDAY_SEED}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_apply_preset_writes_every_setting(name, monkeypatch):
    state = {}
    monkeypatch.setattr(P.st, "session_state", state)
    P.apply_preset(name)
    assert {k: state[sk] for k, sk in P.PRESET_KEYS.items()} == {k: C.PRESETS[name][k] for k in P.PRESET_KEYS}
    assert P.aktives_preset() == name
