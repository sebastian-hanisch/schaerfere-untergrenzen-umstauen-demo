"""Kern: vier Untergrenzen für das restricted Block Relocation Problem und die Suche (IDA* mit Zustandsmerken, Stück 5 und 6), in der die Untergrenze austauschbar ist.

Eine Bucht besteht aus Stapeln (Tupel von unten nach oben). Die Abrufnummer 1 kommt zuerst dran; nur der oberste Container eines Stapels ist erreichbar.
Liegt die nächste Nummer nicht oben, wird der oberste Container ihres Stapels (ein Blocker über dem Ziel) auf einen anderen Stapel mit Platz gesetzt, jeder Hub kostet 1;
die nächste Nummer wird kostenlos entnommen, sobald sie oben liegt (restricted: nur Container über dem gesuchten werden bewegt).

Zustand = Bucht nach dem Abruf; nächster Abruf t im Stapel i; B = die Container über t (oben zuerst); m_k = früheste Abrufnummer in Stapel k (leer: unendlich).

  lb1   Zahl der blockierenden Container (Stück 2).
  lb2   lb1 plus die Zahl der Container c in B mit c > max über k != i von m_k: für sie gibt es keinen sicheren Stapel, sie blockieren nach dem Umsetzen erneut.
  lb3   lb1 plus das Minimum über alle Platzierungsfolgen von B (oben zuerst, nur Stapel mit Platz) der Zahl der Platzierungen auf einen Stapel mit früherem Container.
  lb4   ein Abrufschritt Vorausschau: |B| plus das Minimum über alle Platzierungsfolgen von lb2 des Zustands nach dem Abruf.
  search   IDA*: Budget = Untergrenze der Wurzel, je Budget eine Tiefensuche mit Abbruch bei g + Untergrenze > Budget; Zustandsmerken je Stufe (kanonisch, bis auf Vertauschen
           der Stapel). Knoten = Aufrufe der Suche, Summe über alle Stufen.
"""

import functools
from dataclasses import dataclass

INF = 10 ** 9
BOUNDS = ("LB1", "LB2", "LB3", "LB4")


def autopop(stacks):
    """Ruft ab, was oben liegt und gerade dran ist. Gibt (neue Stapel, abgerufene Nummern in Reihenfolge) zurück."""
    st = [list(s) for s in stacks]
    popped = []
    while True:
        present = [c for s in st for c in s]
        if not present:
            return tuple(tuple(s) for s in st), popped
        t = min(present)
        for s in st:
            if s and s[-1] == t:
                s.pop()
                popped.append(t)
                break
        else:
            return tuple(tuple(s) for s in st), popped


def stack_blockers(stack):
    """Container in einem Stapel (unten nach oben), die über einem früher abzurufenden liegen."""
    total, lowest = 0, INF
    for c in stack:
        if c > lowest:
            total += 1
        else:
            lowest = c
    return total


def blocker_count(stacks):
    """Zahl der blockierenden Container (Untergrenze der Hubzahl, Stück 2)."""
    return sum(stack_blockers(s) for s in stacks)


def target_stack(stacks):
    """(nächste Abrufnummer, Index ihres Stapels). Die Bucht darf nicht leer sein."""
    t = min(c for s in stacks for c in s)
    for i, s in enumerate(stacks):
        if t in s:
            return t, i


def canon(stacks):
    """Kanonische Form: die Stapel sortiert."""
    return tuple(sorted(stacks))


def stack_min(stack):
    """Früheste Abrufnummer im Stapel; leer = unendlich."""
    return min(stack) if stack else INF


def blockers_above_target(stacks):
    """(Ziel, Stapel des Ziels, Container über dem Ziel oben zuerst). Die Bucht darf nicht leer sein."""
    t, i = target_stack(stacks)
    s = stacks[i]
    return t, i, list(reversed(s[s.index(t) + 1:]))


def lb1(stacks, height=None):
    return blocker_count(stacks)


def lb2(stacks, height=None):
    if not any(stacks):
        return 0
    _, i, blk = blockers_above_target(stacks)
    base = blocker_count(stacks)
    if not blk:
        return base
    others = [stack_min(s) for k, s in enumerate(stacks) if k != i]
    top = max(others) if others else -1
    return base + sum(1 for c in blk if c > top)


def lb3(stacks, height):
    if not any(stacks):
        return 0
    _, i, blk = blockers_above_target(stacks)
    base = blocker_count(stacks)
    if not blk:
        return base
    start = tuple(sorted((stack_min(s), len(s)) for k, s in enumerate(stacks) if k != i))

    @functools.lru_cache(maxsize=None)
    def rec(idx, state):
        if idx == len(blk):
            return 0
        c = blk[idx]
        best, seen = INF, set()
        for j, (m, n) in enumerate(state):
            if n >= height or (m, n) in seen:
                continue
            seen.add((m, n))
            new = list(state)
            new[j] = (min(m, c), n + 1)
            best = min(best, (1 if m < c else 0) + rec(idx + 1, tuple(sorted(new))))
        return best

    extra = rec(0, start)
    return INF if extra >= INF else base + extra


def lb4(stacks, height):
    if not any(stacks):
        return 0
    _, i, blk = blockers_above_target(stacks)
    if not blk:
        return lb2(stacks, height)
    best = INF

    def rec(idx, cur):
        nonlocal best
        if idx == len(blk):
            best = min(best, len(blk) + lb2(autopop(cur)[0], height))
            return
        seen = set()
        for j in range(len(cur)):
            if j == i or len(cur[j]) >= height or cur[j] in seen:
                continue
            seen.add(cur[j])
            new = [list(x) for x in cur]
            new[i].pop()
            new[j].append(blk[idx])
            rec(idx + 1, tuple(tuple(x) for x in new))

    rec(0, tuple(tuple(x) for x in stacks))
    return best


BOUND_FUNCS = {"LB1": lb1, "LB2": lb2, "LB3": lb3, "LB4": lb4}


def bound_values(stacks, height):
    """Alle vier Untergrenzen des Zustands (nach dem Abruf) in der Reihenfolge von BOUNDS."""
    st, _ = autopop(stacks)
    return {name: BOUND_FUNCS[name](st, height) for name in BOUNDS}


def _fit_key(stacks, j, c):
    m = stack_min(stacks[j])
    return (0, m) if m > c else (1, -m)


def child_targets(stacks, src, height, c):
    """Zielstapel für den Blocker c (Stapel `src`, Bucht ohne c) in der Reihenfolge der engsten Passung (Stück 1); nur Stapel mit Platz."""
    dests = [j for j in range(len(stacks)) if j != src and len(stacks[j]) < height]
    dests.sort(key=lambda j: (_fit_key(stacks, j, c), j))
    return dests


@dataclass(frozen=True)
class SearchResult:
    optimum: int | None     # None, wenn das Knotenlimit erreicht wurde
    nodes: int              # Zahl der besuchten Knoten (bei capped: das Limit); Summe über alle Budgetstufen
    capped: bool
    stages: int             # Zahl der Budgetstufen (bei capped: die begonnenen)


class _CapReached(Exception):
    pass


class _Found(Exception):
    pass


def search(stacks, height, bound="LB2", cap=1_000_000) -> SearchResult:
    """IDA* mit der gewählten Untergrenze und Zustandsmerken (kanonisch), engste Passung zuerst."""
    lb = BOUND_FUNCS[bound]
    start = tuple(tuple(s) for s in stacks)
    budget = lb(autopop(start)[0], height)
    total, stages = 0, 0
    while True:
        stages += 1
        b = budget
        nodes = [0]
        table = {}
        found = []

        def rec(state, g):
            nodes[0] += 1
            if total + nodes[0] > cap:
                raise _CapReached
            st, _ = autopop(state)
            if not any(st):
                found.append(g)
                raise _Found
            if g + lb(st, height) > b:
                return
            key = canon(st)
            if table.get(key, INF) <= g:
                return
            table[key] = g
            _, i = target_stack(st)
            lst = [list(s) for s in st]
            c = lst[i].pop()
            base = tuple(tuple(s) for s in lst)
            for j in child_targets(base, i, height, c):
                nxt = [list(s) for s in lst]
                nxt[j].append(c)
                rec(tuple(tuple(s) for s in nxt), g + 1)

        try:
            rec(start, 0)
        except _Found:
            pass
        except _CapReached:
            return SearchResult(None, cap, True, stages)
        total += nodes[0]
        if found:
            return SearchResult(found[0], total, False, stages)
        budget += 1
