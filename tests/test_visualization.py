"""Abbildungen an synthetischen Daten: Werte, Farben, gesperrte Achsen, Logarithmusachsen ohne add_hline (DEMO-PLAYBOOK §12)."""

import plotly.graph_objects as go

import sgu_algorithm as A
import sgu_constants as C
import sgu_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def test_blocker_cells_by_hand():
    assert V.blocker_cells(((1, 5), (2, 3), (4, 6))) == {(0, 1), (1, 1), (2, 1)}
    assert V.blocker_cells(((1, 2, 3), (), (4,))) == {(0, 1), (0, 2)}
    assert V.blocker_cells(((5, 3), (2, 1))) == set()


def test_bay_chart_colours_texts_and_the_height_line():
    fig = V.build_bay(((1, 5), (2, 3), (4, 6)), 4, target=1)
    assert _locked(fig) and len(fig.data) == 4 and list(fig.layout.yaxis.range) == [0, 4.35]
    assert list(fig.data[0].marker.color) == [C.COLOR_TARGET, C.COLOR_CELL, C.COLOR_CELL] and list(fig.data[0].text) == ["1", "2", "4"]
    assert list(fig.data[1].marker.color) == [C.COLOR_BLOCK, C.COLOR_BLOCK, C.COLOR_BLOCK] and list(fig.data[2].y) == [0, 0, 0]
    assert [s.y0 for s in fig.layout.shapes] == [4] and list(fig.layout.xaxis.ticktext) == ["Stapel 1", "Stapel 2", "Stapel 3"]


def _hits(n, hit, gap):
    return {"n": n, "hit": dict(zip(A.BOUNDS, hit)), "gap_mean": dict(zip(A.BOUNDS, gap))}


def _cells():
    return {"4,4": _hits(100, (4, 24, 24, 37), (3.0, 1.56, 1.55, 1.04)), "3,2": _hits(100, (67, 100, 100, 100), (0.33, 0.0, 0.0, 0.0)), "3,3": _hits(100, (19, 57, 59, 73), (1.52, 0.64, 0.61, 0.34))}


def test_hits_chart_is_ordered_by_container_count_and_in_percent():
    fig = V.build_hits(_cells())
    assert _locked(fig) and list(fig.layout.yaxis.range) == [0, 105] and not fig.layout.shapes
    assert list(fig.data[0].x) == ["3 × 2", "3 × 3", "4 × 4"] and [t.name for t in fig.data] == list(A.BOUNDS)
    assert list(fig.data[0].y) == [67.0, 19.0, 4.0] and list(fig.data[1].y) == [100.0, 57.0, 24.0] and list(fig.data[3].y) == [100.0, 73.0, 37.0]
    assert [t.marker.color for t in fig.data] == [C.COLOR_LINES[k] for k in A.BOUNDS]


def test_gap_chart_shows_the_mean_gap():
    fig = V.build_gap(_cells())
    assert _locked(fig) and list(fig.data[0].y) == [0.33, 1.52, 3.0] and list(fig.data[3].y) == [0.0, 0.34, 1.04] and fig.layout.yaxis.rangemode == "tozero"


def _search():
    return {"4,3": {"nodes": {k: {"median": m} for k, m in zip(A.BOUNDS, (14.0, 8.0, 8.0, 7.0))}, "ms": dict(zip(A.BOUNDS, (0.3, 0.2, 0.5, 0.9)))},
            "3,3": {"nodes": {k: {"median": m} for k, m in zip(A.BOUNDS, (16.0, 8.0, 8.0, 6.0))}, "ms": dict(zip(A.BOUNDS, (0.3, 0.2, 0.4, 0.5)))}}


def test_node_and_time_charts_use_log_axes_without_hline():
    n, t = V.build_nodes(_search()), V.build_time(_search())
    for fig in (n, t):
        assert _locked(fig) and fig.layout.yaxis.type == "log" and not fig.layout.shapes and list(fig.data[0].x) == ["3 × 3", "4 × 3"]
    assert list(n.data[0].y) == [16.0, 14.0] and list(n.data[3].y) == [6.0, 7.0] and list(t.data[1].y) == [0.2, 0.2] and list(t.data[3].y) == [0.5, 0.9]


def test_all_figures_are_plotly_figures():
    assert all(isinstance(f, go.Figure) for f in (V.build_bay(((1,),), 2), V.build_hits(_cells()), V.build_gap(_cells()), V.build_nodes(_search()), V.build_time(_search())))
