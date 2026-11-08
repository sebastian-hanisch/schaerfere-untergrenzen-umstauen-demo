"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

STACKS_MIN, STACKS_MAX, DEFAULT_STACKS = 3, 5, 3          # Zahl der Stapel
LAYERS_MIN, LAYERS_MAX, DEFAULT_LAYERS = 2, 4, 3          # Anfangsfüllung je Stapel (Lagen)
EXTRA_MIN, EXTRA_MAX, DEFAULT_EXTRA = 1, 4, 2             # Platz: Höchsthöhe = Lagen + Zuschlag (Standard 2 wie in Stück 1 bis 8)
SEED_MAX = 999999

REF_CAP = 300_000                                         # Knotenlimit der Suche mit LB2, die das Optimum liefert (Bezugswert)
LIVE_CAP = 40_000                                         # Knotenlimit der Suchläufe mit den anderen Schranken (live)

# Zellen der vorberechneten Tabellen: (Stapel, Lagen, Zahl der festen Buchten). Dieselben Buchten wie in Stück 4 bis 8 (Seeds ab 0, Platz 2).
HIT_CELLS = ((3, 2, 100), (4, 2, 100), (3, 3, 100), (4, 3, 100), (5, 3, 100), (3, 4, 100), (4, 4, 100), (5, 4, 100))     # Stärke der Schranken (A)
SEARCH_CELLS = ((3, 3, 100), (4, 3, 100), (5, 3, 60), (4, 4, 60), (5, 4, 40))                                            # Suche mit jeder Schranke (C)
TWO_LAYER_CELLS = ((4, 2, 1500), (5, 2, 300), (6, 2, 100))                                                               # zwei Lagen (B); Seeds ab TWO_LAYER_SEED0
TWO_LAYER_SEED0 = 1000

# Schwellen der Verdikte
HIT_SHARE_ALMOST = 0.9                                    # Verdikt „fast vollständig“: Anteil der Buchten, in denen LB2 das Optimum trifft, ab hier
NODE_GAIN = 1.5                                           # „spart Knoten“: Median der Knoten mit LB1 / mit der Schranke mindestens so groß
TIME_FACTOR = 1.0                                         # „spart Zeit“: Zeit mit der Schranke höchstens so groß wie mit LB1 (Verhältnis)

COLOR_CELL = "#7a8fa6"
COLOR_BLOCK = "#b5545a"        # blockierend (liegt über einem früher abzurufenden)
COLOR_TARGET = "#2F6B65"       # nächster Abruf
COLOR_LINES = {"LB1": "#7a8fa6", "LB2": "#2F6B65", "LB3": "#d9822b", "LB4": "#4c78a8"}
COLOR_OPT = "#1c4742"

# Sonderbuchten (in der Vormessung gefunden, Eigenschaften in tests/test_presets.py festgehalten)
EVERYDAY_SEED = 12     # 3 x 3, Platz 2: LB1 4, LB2 4, LB3 4, LB4 5 = Optimum 5
GAP_SEED = 27          # 3 x 3, Platz 2: alle vier Schranken 5, Optimum 6: die Lücke bleibt
BIG_GAIN_SEED = 0      # 4 x 4, Platz 2: LB1 7, LB2 10 = Optimum 10
TWO_LAYER_SEED = 3     # 4 x 2, Platz 2: LB1 2, LB2 3 = Optimum 3
MISS_SEED = 100        # 3 x 2, Platz 2: (3, 6), (1, 5), (4, 2): LB1 2, LB2 bis LB4 3, Optimum 4 (der eine Fehlschlag von LB2 unter allen Buchten 3 x 2)
COST_SEED = 0          # 5 x 4, Platz 2: LB1 14, LB2 bis LB4 16, Optimum 18; mit LB4 knapp ein Drittel der Knoten, aber um ein Vielfaches länger
HAND_BAY = ((1, 5), (2, 3), (4, 6))                       # die Bucht von Hand (Stück 2: drei Blocker), Höchsthöhe 4
HAND_HEIGHT = 4
MISS_BAY = ((1, 5), (3, 6), (4, 2))                        # der eine Fehlschlag von LB2 unter den 120 Buchten 3 x 2, Höchsthöhe 4
MISS_HEIGHT = 4

PRESETS = {
    "Alltag (3 Stapel, 3 Lagen)": {"stacks": 3, "layers": 3, "extra": DEFAULT_EXTRA, "seed": EVERYDAY_SEED},
    "Zwei Lagen: LB2 reicht (4 Stapel, 2 Lagen)": {"stacks": 4, "layers": 2, "extra": DEFAULT_EXTRA, "seed": TWO_LAYER_SEED},
    "LB2 schließt die Lücke (4 Stapel, 4 Lagen)": {"stacks": 4, "layers": 4, "extra": DEFAULT_EXTRA, "seed": BIG_GAIN_SEED},
    "Die Lücke bleibt (3 Stapel, 3 Lagen)": {"stacks": 3, "layers": 3, "extra": DEFAULT_EXTRA, "seed": GAP_SEED},
    "LB2 verfehlt (3 Stapel, 2 Lagen)": {"stacks": 3, "layers": 2, "extra": DEFAULT_EXTRA, "seed": MISS_SEED},
    "Schärfer lohnt nicht (5 Stapel, 4 Lagen)": {"stacks": 5, "layers": 4, "extra": DEFAULT_EXTRA, "seed": COST_SEED},
}
PRESET_HELP = {
    "Alltag (3 Stapel, 3 Lagen)": "9 Container: LB1 und LB2 liegen bei 4, erst die Vorausschau (LB4) trifft das Optimum 5.",
    "Zwei Lagen: LB2 reicht (4 Stapel, 2 Lagen)": "8 Container: LB1 liegt bei 2, LB2 trifft das Optimum 3 ohne jede Suche.",
    "LB2 schließt die Lücke (4 Stapel, 4 Lagen)": "16 Container: LB1 liegt bei 7, LB2 trifft das Optimum 10: drei Hübe der Lücke durch das Zählen der Blocker ohne sicheren Stapel.",
    "Die Lücke bleibt (3 Stapel, 3 Lagen)": "9 Container: alle vier Schranken liegen bei 5, das Optimum ist 6; die Lücke kommt aus späteren Abrufschritten.",
    "LB2 verfehlt (3 Stapel, 2 Lagen)": "6 Container: der eine Fehlschlag von LB2 unter allen 120 Buchten 3 × 2 (bis auf Vertauschen der Stapel): LB2 liegt bei 3, das Optimum ist 4.",
    "Schärfer lohnt nicht (5 Stapel, 4 Lagen)": "20 Container: LB4 braucht deutlich weniger Knoten als LB1, die Suche dauert aber um ein Vielfaches länger; die Zeit steht in der Tabelle.",
}
