"""Orakel-Test schaerfere-untergrenzen-umstauen-demo (ORACLE-PLAYBOOK, DEMO-PLAYBOOK §12): Zulässigkeit, Dominanz und Werte der Schranken gegen ANDERE Rechenwege.

Eigene, unabhängige Umsetzungen im Test: (a) das Restoptimum jedes Zustands per vollständiger Rekursion über alle Platzierungen (ohne Untergrenze, ohne IDA*), (b) LB2, LB3 und LB4
per Ausprobieren aller Platzierungsfolgen mit kopierten Zuständen. Vorher an den Handzahlen geprüft: Hand-Bucht LB1 3, LB2 bis LB4 4, Optimum 4."""

import functools
import itertools
import random

import pytest

import sgu_algorithm as A
from sgu_scenario import make_bay

INF = 10 ** 9


def pop_all(state):
    """Eigener Abruf: entnimmt die nächste Nummer, solange sie oben liegt."""
    st = [list(s) for s in state]
    while True:
        nums = [c for s in st for c in s]
        if not nums:
            return tuple(tuple(s) for s in st)
        t = min(nums)
        k = next(i for i, s in enumerate(st) if t in s)
        if st[k][-1] != t:
            return tuple(tuple(s) for s in st)
        st[k].pop()


def moves(state, height):
    """Alle erlaubten Hübe: der oberste Container des Stapels mit der nächsten Nummer auf jeden anderen Stapel mit Platz. Gibt die Folgezustände (nach dem Abruf) zurück."""
    nums = [c for s in state for c in s]
    t = min(nums)
    k = next(i for i, s in enumerate(state) if t in s)
    out = []
    for j in range(len(state)):
        if j != k and len(state[j]) < height:
            new = [list(s) for s in state]
            new[j].append(new[k].pop())
            out.append(pop_all(new))
    return out


@functools.lru_cache(maxsize=None)
def exact_cost(state, height):
    """Restoptimum eines Zustands (nach dem Abruf) durch vollständige Rekursion; kanonisch gemerkt."""
    if not any(state):
        return 0
    best = INF
    for nxt in moves(state, height):
        best = min(best, 1 + exact_cost(tuple(sorted(nxt)), height))
    return best


def opt(bay, height):
    return exact_cost(tuple(sorted(pop_all(bay))), height)


def blockers(state):
    out = 0
    for s in state:
        lowest = INF
        for c in s:
            if c > lowest:
                out += 1
            else:
                lowest = c
    return out


def above(state):
    nums = [c for s in state for c in s]
    t = min(nums)
    k = next(i for i, s in enumerate(state) if t in s)
    s = state[k]
    return k, [c for c in reversed(s[s.index(t) + 1:])]


def ref_lb2(state):
    if not any(state):
        return 0
    k, blk = above(state)
    others = [min(s) if s else INF for j, s in enumerate(state) if j != k]
    return blockers(state) + sum(1 for c in blk if all(m < c for m in others))


def placements(state, height, k, blk):
    """Alle Platzierungsfolgen der Container in blk (oben zuerst): Liste von (Zustand nach dem Umsetzen, Zahl der Platzierungen auf einen Stapel mit früherem Container)."""
    out = []
    for dest in itertools.product([j for j in range(len(state)) if j != k], repeat=len(blk)):
        st = [list(s) for s in state]
        bad, ok = 0, True
        for c, j in zip(blk, dest):
            st[k].pop()
            if len(st[j]) >= height:
                ok = False
                break
            if st[j] and min(st[j]) < c:
                bad += 1
            st[j].append(c)
        if ok:
            out.append((tuple(tuple(s) for s in st), bad))
    return out


def ref_lb3(state, height):
    if not any(state):
        return 0
    k, blk = above(state)
    if not blk:
        return blockers(state)
    pl = placements(state, height, k, blk)
    return blockers(state) + min(bad for _, bad in pl) if pl else INF


def ref_lb4(state, height):
    if not any(state):
        return 0
    k, blk = above(state)
    if not blk:
        return ref_lb2(state)
    pl = placements(state, height, k, blk)
    return min(len(blk) + ref_lb2(pop_all(s)) for s, _ in pl) if pl else INF


def states_of(stacks, layers, seeds, steps, height, rng):
    """Wurzeln und zufällig erreichte Zustände (nach dem Abruf) mehrerer Buchten, je mit der Höchsthöhe."""
    out = []
    for sd in seeds:
        st = pop_all(make_bay(stacks, layers, sd))
        for _ in range(steps):
            if not any(st):
                break
            out.append((st, height))
            st = rng.choice(moves(st, height))
    return out


def all_3x2():
    return sorted({tuple(sorted(tuple(p[i * 2:(i + 1) * 2]) for i in range(3))) for p in itertools.permutations(range(1, 7))})


def test_the_independent_optimum_matches_the_search_on_all_bays_3x2():
    bays = all_3x2()
    assert len(bays) == 120
    for bay in bays:
        assert opt(bay, 4) == A.search(bay, 4, "LB1").optimum == A.search(bay, 4, "LB4").optimum


def test_every_bound_is_admissible_in_every_reachable_state_3x2_and_samples():
    """Kein Zustand, in dem eine Schranke über dem unabhängig berechneten Restoptimum liegt (Zulässigkeit; Zustände: alle aus allen 120 Buchten 3 x 2 erreichbaren, dazu Stichproben)."""
    rng = random.Random(7)
    reach = set()
    todo = [pop_all(b) for b in all_3x2()]
    while todo:
        st = todo.pop()
        key = tuple(sorted(st))
        if key in reach or not any(st):
            continue
        reach.add(key)
        todo.extend(moves(st, 4))
    assert len(reach) > 150
    cases = [(st, 4) for st in sorted(reach)]
    cases += states_of(4, 2, range(40), 4, 4, rng) + states_of(3, 3, range(40), 5, 5, rng) + states_of(4, 3, range(15), 6, 5, rng) + states_of(3, 3, range(30), 4, 4, rng)
    for st, h in cases:
        e = exact_cost(tuple(sorted(st)), h)
        v = {k: A.BOUND_FUNCS[k](st, h) for k in A.BOUNDS}
        assert all(x <= e for x in v.values()), (st, h, v, e)
        assert v["LB1"] <= v["LB2"] <= v["LB3"] <= v["LB4"], (st, v)


def test_lb2_lb3_lb4_equal_the_brute_force_versions_on_many_states():
    rng = random.Random(3)
    checked = 0
    for stacks, layers, h, n, steps in ((3, 2, 4, 60, 4), (3, 3, 5, 60, 5), (4, 2, 4, 60, 4), (4, 3, 5, 30, 6), (3, 3, 4, 40, 4)):
        for st, _ in states_of(stacks, layers, range(n), steps, h, rng):
            assert A.lb1(st) == blockers(st)
            assert A.lb2(st) == ref_lb2(st), st
            assert A.lb3(st, h) == ref_lb3(st, h), (st, h)
            assert A.lb4(st, h) == ref_lb4(st, h), (st, h)
            checked += 1
    assert checked > 700


def test_lb2_is_exact_on_every_bay_3x2_but_one_and_on_every_bay_4x2_in_the_sample():
    miss = [bay for bay in all_3x2() if A.bound_values(bay, 4)["LB2"] != opt(bay, 4)]
    assert miss == [((1, 5), (3, 6), (4, 2))]
    assert sum(1 for bay in all_3x2() if A.bound_values(bay, 4)["LB1"] != opt(bay, 4)) == 44
    for sd in range(150):
        bay = make_bay(4, 2, 1000 + sd)
        assert A.bound_values(bay, 4)["LB2"] == opt(bay, 4)


def test_the_height_limit_makes_lb3_stronger_and_it_stays_admissible():
    bay = ((1, 3, 6), (7, 9, 8), (5, 4, 2))                                         # Höchsthöhe 4: LB3 5 (Optimum 5); ohne Platzgrenze nur 4
    assert A.lb3(bay, 4) == 5 == opt(bay, 4) and A.lb3(bay, 99) == 4 and ref_lb3(bay, 4) == 5


@pytest.mark.parametrize("sd", range(8))
def test_search_optimum_is_the_independent_optimum_on_3x3(sd):
    bay = make_bay(3, 3, sd)
    assert opt(bay, 5) == A.search(bay, 5, "LB1").optimum == A.search(bay, 5, "LB3").optimum
