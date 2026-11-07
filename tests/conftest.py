"""Gemeinsame Fixtures: die Buchten, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand():
    """Die Bucht von Hand: (1, 5), (2, 3), (4, 6), Höchsthöhe 4 (von unten nach oben). Blocker: 5, 3 und 6, also LB1 = 3. Ziel 1: Blocker über dem Ziel [5]; früheste Abrufnummern der anderen
    Stapel 2 und 4: die 5 ist größer als beide, kein sicherer Stapel, LB2 = 4. LB3: beide Plätze schlecht, 4. LB4: nach dem Umsetzen der 5 auf Stapel 2 oder 3 liegen im Folgezustand drei
    Blocker (3, 5 bzw. 3, 5 und 6), mit dem leeren Stapel 1 kein weiterer Zuschlag: 1 + 3 = 4. Optimum 4."""
    return ((1, 5), (2, 3), (4, 6)), 4


@pytest.fixture
def counter():
    """Das Gegenbeispiel aus Stück 1: (3, 6), (2, 4), (1, 5), Höchsthöhe 4. LB1 = 3, die 5 über der 1 hat keinen sicheren Stapel (Minima 2 und 3): LB2 = 4 = Optimum."""
    return ((3, 6), (2, 4), (1, 5)), 4


@pytest.fixture
def miss():
    """Der eine Fehlschlag von LB2 unter den 120 Buchten 3 x 2: (1, 5), (3, 6), (4, 2), Höchsthöhe 4. LB1 = 2 (die 5 und die 6), LB2 = 3 (die 5 hat keinen sicheren Stapel), Optimum 4."""
    return ((1, 5), (3, 6), (4, 2)), 4
