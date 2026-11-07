"""Inhalt der App an festen Fällen (DEMO-PLAYBOOK §12): was im Ergebnis, in den Tabellen und in den Verdikten steht."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(preset=None):
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    if preset:
        at.sidebar.button(key=f"preset_{preset}").click().run()
        assert not at.exception, [str(e) for e in at.exception]
    return at


def _text(at):
    return "\n".join(e.value for kind in (at.markdown, at.caption, at.info, at.success, at.warning) for e in kind)


def _metrics(at):
    return {m.label: (m.value, m.delta) for m in at.metric}


def test_default_page_has_the_sections_and_the_everyday_result():
    at = _run()
    subs = [s.value for s in at.subheader]
    assert [s for s in subs if s.startswith("🔬")] == [
        "🔬 Experiment: Die Schranke von Hand", "🔬 Experiment: Wie oft trifft die Schranke das Optimum?", "🔬 Experiment: Zwei Lagen", "🔬 Experiment: Was hat die Suche davon?"]
    assert "🚧 Wo die Annahmen enden" in subs
    m = _metrics(at)
    assert m["LB1"] == ("4", "Lücke 1") and m["LB2"] == ("4", "Lücke 1") and m["LB3"] == ("4", "Lücke 1") and m["LB4"] == ("5", "Lücke 0") and m["Optimum"][0] == "5"
    assert any(s.value.startswith("Die erste Schranke, die das Optimum 5 trifft, ist LB4") for s in at.success)


def test_default_page_tables_quote_the_stored_numbers():
    text = _text(_run())
    assert "| 3 × 3 (100) | 5,05 | 19 | 57 | 59 | 73 |" in text and "| 3 × 2 (100) | 1,74 | 67 | 100 | 100 | 100 |" in text and "| 5 × 4 (100) | 12,52 | 3 | 19 | 19 | 28 |" in text
    assert "| 3 × 2, alle (120) | 44 | 1 | 1 | 1 |" in text and "| 4 × 2 (1500) | 489 | 0 | 0 | 0 |" in text and "| 6 × 2 (100) | 26 | 0 | 0 | 0 |" in text
    assert "| 5 × 4 (40) | 284 / 56 710 | 134,5 / 28 017 | 120,5 / 26 641 | 56 / 11 239 |" in text and "| 3 × 3 (100) | 16 / 123 | 8 / 70 | 8 / 45 | 6 / 36 |" in text


def test_hand_section_reports_the_hand_bay_and_the_miss():
    text = _text(_run())
    assert "kommt auf **3**" in text and "LB2 = 3 + 1 = **4**; das Optimum ist **4**" in text and "| 5 | Stapel 2: 2, Stapel 3: 4 | nein |" in text
    assert "(1, 5), (3, 6), (4, 2), Höchsthöhe 4. LB2 liegt bei 3, das Optimum ist 4" in text


def test_custom_cell_note_for_the_default_cell():
    text = _text(_run())
    assert "**Zelle 3 × 3 (Ihre Einstellung)**:" in text and "**Zelle 3 × 3 (Ihre Einstellung):**" in text


def test_gap_preset_shows_a_warning():
    at = _run("Die Lücke bleibt (3 Stapel, 3 Lagen)")
    assert any(w.value.startswith("Keine der vier Schranken trifft das Optimum 6") for w in at.warning)
    assert all(_metrics(at)[k][0] == "5" for k in ("LB1", "LB2", "LB3", "LB4")) and _metrics(at)["Optimum"][0] == "6"


def test_big_gain_preset_shows_lb2_as_the_first_hit():
    at = _run("LB2 schließt die Lücke (4 Stapel, 4 Lagen)")
    assert any("ist LB2 (LB1 7, LB2 10" in s.value for s in at.success) and _metrics(at)["LB1"] == ("7", "Lücke 3")


@pytest.mark.parametrize("stacks,layers", [(5, 2), (3, 4)])
def test_cells_with_and_without_stored_search_bands_do_not_crash(stacks, layers):
    at = _run()
    at.sidebar.slider(key="stacks_slider").set_value(stacks).run()
    at.sidebar.slider(key="layers_slider").set_value(layers).run()
    assert not at.exception
    assert any("wurde die Suche nicht vorberechnet" in i.value for i in at.info)
