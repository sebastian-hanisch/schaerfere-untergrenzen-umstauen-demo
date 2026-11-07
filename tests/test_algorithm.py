"""Die Untergrenzen und die Suche gegen Handrechnung (DEMO-PLAYBOOK §1b und §12)."""

import pytest

import sgu_algorithm as A
from sgu_scenario import make_bay


def test_autopop_target_stack_and_blockers():
    assert A.autopop(((1,), (2,))) == (((), ()), [1, 2])
    assert A.autopop(((2, 1), (3,))) == (((), ()), [1, 2, 3])                      # die 1 liegt oben, dann die 2, dann die 3
    st, popped = A.autopop(((7, 1, 4), (2, 3, 9), (6, 5, 8)))
    assert st == ((7, 1, 4), (2, 3, 9), (6, 5, 8)) and popped == []                 # die 1 liegt unter der 4: nichts wird abgerufen
    assert A.target_stack(st) == (1, 0) and A.blockers_above_target(st) == (1, 0, [4])
    assert A.stack_blockers((7, 1, 4)) == 1 and A.stack_blockers((2, 3, 9)) == 2 and A.stack_blockers((6, 5, 8)) == 1 and A.blocker_count(st) == 4
    assert A.stack_min(()) == A.INF and A.stack_min((7, 1, 4)) == 1 and A.canon(((3,), (1,))) == ((1,), (3,))


def test_bounds_by_hand(hand, counter, miss):
    assert A.bound_values(*hand) == {"LB1": 3, "LB2": 4, "LB3": 4, "LB4": 4}
    assert A.bound_values(*counter) == {"LB1": 3, "LB2": 4, "LB3": 4, "LB4": 4}
    assert A.bound_values(*miss) == {"LB1": 2, "LB2": 3, "LB3": 3, "LB4": 3}
    assert [A.search(b, h, "LB2").optimum for b, h in (hand, counter, miss)] == [4, 4, 4]


def test_lb2_counts_blockers_without_a_safe_stack():
    st = ((1, 5), (2, 3), (4, 6))
    assert A.lb1(st) == 3 and A.lb2(st) == 4                                       # die 5: Minima 2 und 4, kein sicherer Stapel
    assert A.lb2(((1, 3), (2, 4), (5, 6))) == A.lb1(((1, 3), (2, 4), (5, 6)))      # die 3 ist kleiner als 5: sicher auf Stapel 3
    assert A.lb2(((1, 5), (2,), ())) == A.lb1(((1, 5), (2,), ()))                  # ein leerer Stapel ist immer sicher (Minimum unendlich)
    assert A.lb2(()) == 0 and A.lb2(((),)) == 0


def test_lb2_counts_every_unsafe_blocker_over_the_target():
    st = ((1, 6, 5), (2, 3), (4, 7))                                                # über der 1: 5 und 6; Minima der anderen: 2 und 4; beide größer als 4
    assert A.blockers_above_target(st) == (1, 0, [5, 6]) and A.lb1(st) == 4 and A.lb2(st) == 6


def test_lb3_plans_the_places_in_order():
    st, h = ((2, 3, 7), (8, 9, 6), (1, 5, 4)), 4                                    # über der 1: 4 (oben) und 5; sicher ist nur Stapel 2 (Minimum 6): die 4 dorthin senkt das Minimum auf 4, die 5 hat dann keinen sicheren Stapel
    assert A.lb1(st) == 5 and A.lb2(st) == 5 and A.lb3(st, h) == 6 and A.lb4(st, h) == 6
    assert A.search(st, h, "LB1").optimum == A.search(st, h, "LB3").optimum == 7
    assert A.lb3(((1, 5, 6), (2,), ()), 4) == A.lb1(((1, 5, 6), (2,), ()))          # 6 auf den leeren Stapel, 5 darauf: kein Zuschlag


def test_lb3_respects_the_height_limit():
    bay = ((1, 3, 6), (7, 9, 8), (5, 4, 2))                                         # über der 1: 6 (oben), 3; Stapel 2 (Minimum 7) hat bei Höchsthöhe 4 nur einen freien Platz
    assert A.lb1(bay) == 4 and A.lb2(bay) == 4 and A.lb3(bay, 4) == 5 and A.lb3(bay, 99) == 4     # ohne Platzgrenze nähmen 6 und 3 beide den Stapel 2: kein Zuschlag


def test_lb4_looks_one_retrieval_ahead():
    st, h = ((7, 1, 4), (2, 3, 9), (6, 5, 8)), 5                                    # Alltags-Bucht: LB1 bis LB3 sind 4, die 4 kann sicher auf Stapel 3, aber dann bleibt die 9 ohne Platz
    assert [A.BOUND_FUNCS[k](st, h) for k in A.BOUNDS] == [4, 4, 4, 5] and A.search(st, h, "LB1").optimum == 5


def test_a_bound_never_exceeds_the_optimum_and_dominance_holds_on_the_hand_bays(hand, counter, miss):
    for bay, h in (hand, counter, miss):
        v = A.bound_values(bay, h)
        opt = A.search(bay, h, "LB1").optimum
        assert v["LB1"] <= v["LB2"] <= v["LB3"] <= v["LB4"] <= opt


def test_all_bounds_find_the_same_optimum_and_more_node_saving_with_a_stronger_bound(hand, counter):
    for bay, h in (hand, counter):
        res = {k: A.search(bay, h, k) for k in A.BOUNDS}
        assert len({r.optimum for r in res.values()}) == 1 and not any(r.capped for r in res.values())
    assert [A.search(*hand, k).nodes for k in A.BOUNDS] == [8, 5, 5, 5]              # gemessene Knotenzahlen der Hand-Bucht (Handzahl: LB1 muss ein Budget mehr ausprobieren)
    assert [A.search(*counter, k).nodes for k in A.BOUNDS] == [15, 10, 8, 8]


def test_search_stages_are_budget_steps_from_the_root_bound(hand):
    r = A.search(*hand, "LB1")
    assert (r.optimum, r.stages) == (4, 2)                                          # Budget 3 (LB1), dann 4
    assert A.search(*hand, "LB2").stages == 1                                       # LB2 startet gleich bei 4 und findet die Lösung im ersten Budget


def test_child_targets_follow_the_tightest_fit_and_respect_capacity():
    base = ((), (2, 3), (4,), (5, 6, 7, 8))                                         # Stapel 4 ist bei Höchsthöhe 4 voll
    assert A.child_targets(base, 0, 4, 1) == [1, 2]                                 # Blocker 1: Stapel 2 (Minimum 2) vor Stapel 3 (Minimum 4); Stapel 4 voll
    assert A.child_targets(base, 1, 4, 9) == [0, 2]                                 # Blocker 9: nur der leere Stapel ist sicher, dann Stapel 3 (Minimum 4 < 9)
    wide = ((9,), (), (4,), (2, 3))
    assert A.child_targets(wide, 0, 5, 1) == [3, 2, 1]                              # alle sicher: kleinstes Minimum zuerst, der leere Stapel (unendlich) zuletzt
    assert A.child_targets(wide, 0, 5, 3) == [2, 1, 3]                              # für die 3: Stapel 3 (Minimum 4) sicher, leer sicher, Stapel 4 (Minimum 2) schlecht


@pytest.mark.parametrize("sd", range(5))
def test_search_with_every_bound_agrees_on_random_bays(sd):
    bay = make_bay(3, 3, sd)
    assert len({A.search(bay, 5, k).optimum for k in A.BOUNDS}) == 1
