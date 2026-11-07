"""Schärfere Untergrenzen: die Lücke von Stück 2 schließen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 9 der Reihe „Umstauen: Untergrenze und Suche“. Die Untergrenze aus Stück 2 zählt jeden Blocker einmal. Hier vier Schranken, die mehr sehen: LB2 zählt die Blocker, die
keinen sicheren Stapel finden, LB3 plant ihre Plätze, LB4 schaut einen Abrufschritt voraus. Die Demo rechnet sie live, misst vorberechnet, wie oft sie das Optimum treffen, und was die
Suche davon hat.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sgu_algorithm as A
import sgu_constants as C
from sgu_evaluation import (
    BOUND_NAMES,
    Settings,
    analyse,
    cell_key,
    dec,
    explain_rows,
    load_bands,
    ms_text,
    num,
    num_f,
    result_rows,
    time_text,
    verdict_bay,
    verdict_hits,
    verdict_search,
    verdict_two,
)
from sgu_layout import dunkles_design, kopf_css
from sgu_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sgu_visualization import build_bay, build_gap, build_hits, build_nodes, build_time

st.set_page_config(page_title="Schärfere Untergrenzen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _bands():
    return load_bands()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sgu_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📏 Schärfere Untergrenzen: die Lücke schließen")
st.markdown(
    """
Stück 2 hat die **Untergrenze** gebaut: jeder **Blocker** (ein Container über einem früher abzurufenden) muss mindestens einmal bewegt werden. Sie übersieht, dass ein Blocker oft **keinen sicheren Platz** findet und ein zweites Mal bewegt werden muss. Hier **vier Schranken**: **LB1** (die Zählung aus Stück 2), **LB2** (zählt die Blocker ohne sicheren Stapel mit), **LB3** (plant die Plätze der Blocker) und **LB4** (schaut einen Abrufschritt voraus). Die Demo **rechnet sie live** auf kleinen Buchten und misst vorberechnet, **wie oft sie das Optimum treffen**, **wie weit die Lücke schrumpft** und **was die Suche davon hat**.

Weiter unten: die Abschnitte **🔬 Experiment** (die Schranke von Hand, wie oft sie das Optimum trifft, zwei Lagen, was die Suche davon hat), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Dies ist das neunte Stück der Reihe „Umstauen: Untergrenze und Suche“.
"""
)

with st.expander("So funktionieren die Schranken", expanded=True):
    st.markdown(
        """
1. **LB1:** Zahl der Blocker. Gültig, weil jeder Blocker mindestens einmal bewegt werden muss.
2. **LB2:** Der nächste Abruf *t* liegt unter einigen Containern (den **Blockern über dem Ziel**). Jeder muss jetzt auf einen anderen Stapel. Ist seine Nummer **größer als der früheste Abruf aller anderen Stapel**, liegt er danach über einem früher abzurufenden Container und muss **ein zweites Mal** bewegt werden: ein zusätzlicher Hub.
3. **LB3:** Wie LB2, aber die Blocker werden der Reihe nach **wirklich platziert** (oben zuerst, nur Stapel mit Platz). Wer zuerst gesetzt wird, senkt die früheste Nummer seines Stapels und nimmt dem nächsten, größeren Blocker dort den sicheren Platz; volle Stapel scheiden aus. Gezählt wird die **kleinste mögliche Zahl** schlechter Platzierungen.
4. **LB4:** Probiert alle Platzierungen der Blocker, ruft *t* ab und nimmt für jeden Folgezustand LB2: **ein Abrufschritt Vorausschau**.
5. Alle vier sind **zulässig** (nie über dem Optimum) und gelten in **jedem** Suchknoten; LB1 ≤ LB2 ≤ LB3 ≤ LB4.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Bucht**")
    stacks = st.slider("Stapel", *bounds("stacks_slider"), key="stacks_slider", help="Wie viele Stapel die Bucht hat.")
    layers = st.slider("Lagen je Stapel", *bounds("layers_slider"), key="layers_slider", help="So viele Container stehen anfangs auf jedem Stapel.")
    extra = st.slider("Platz (Lagen über der Anfangshöhe)", *bounds("extra_slider"), key="extra_slider",
                      help="Höchsthöhe = Lagen + Platz. Standard 2. Die vorberechneten Tabellen gelten für Platz 2.")
    seed = st.number_input("Bucht-Nummer (Seed)", *bounds("seed_input"), key="seed_input", step=1, help="Die Nummer bestimmt, wie die Abrufnummern auf die Plätze verteilt sind.")
    st.button("🎲 Neue Bucht würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"stacks_slider": int(stacks), "layers_slider": int(layers), "extra_slider": int(extra), "seed_input": int(seed)})

settings = Settings(int(stacks), int(layers), int(extra), int(seed))
with st.spinner("Rechne die vier Schranken und die Suche mit jeder …"):
    a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
cols = st.columns(5)
for col, k in zip(cols, A.BOUNDS):
    col.metric(k, a.bounds[k], delta="–" if a.optimum is None else f"Lücke {a.optimum - a.bounds[k]}", delta_color="off", help=BOUND_NAMES[k])
cols[4].metric("Optimum", "nicht bewiesen" if a.optimum is None else a.optimum, delta=f"Bucht {settings.stacks} × {settings.layers}, {a.containers} Container", delta_color="off",
               help="Aus der Suche mit LB2 (Bezugswert).")
st.plotly_chart(build_bay(a.bay, a.height, target=min(c for s in a.bay for c in s)), width="stretch", key="chart_bay")
st.caption("Rot: blockierende Container (liegen über einem früher abzurufenden), grün: der nächste Abruf, grau-blau: alle übrigen.")
table = ["| Schranke | Wert | Lücke zum Optimum | Suche mit dieser Schranke |", "|---|---|---|---|"]
for r in result_rows(a):
    table.append(f"| {r['name']} | {r['value']} | {r['gap']} | {r['effort']} |")
st.markdown("\n".join(table))
st.caption("Zeiten sind Einzelmessungen auf dem Rechner dieser Sitzung und schwanken (Python). Die Suche ist IDA* mit Zustandsmerken aus Stück 5 und 6; Knoten = Aufrufe der Suche.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie weit schließt die Schärfe die Lücke?")
kind, text = verdict_bay(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: die Schranke von Hand -----------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Die Schranke von Hand")
hand = C.HAND_BAY
hv = A.bound_values(hand, C.HAND_HEIGHT)
st.caption("3 Stapel mit je 2 Containern, Höchsthöhe 4, von unten nach oben (1, 5), (2, 3), (4, 6). Nummer 1 kommt zuerst: Die 5 liegt darüber und muss weg. "
           f"LB1 zählt 3 Blocker (die 5, die 3 und die 6) und kommt auf **{hv['LB1']}**.")
st.plotly_chart(build_bay(hand, C.HAND_HEIGHT, target=1), width="stretch", key="chart_hand")
ht = ["| Blocker über dem Ziel 1 | früheste Abrufnummern der anderen Stapel | sicherer Stapel? |", "|---|---|---|"]
for r in explain_rows(hand, C.HAND_HEIGHT):
    ht.append(f"| {r['blocker']} | {r['others']} | {'ja' if r['safe'] else 'nein'} |")
st.markdown("\n".join(ht))
hopt = A.search(hand, C.HAND_HEIGHT, "LB2").optimum
st.success(f"Die 5 ist größer als 2 und als 4: Wohin sie auch kommt, liegt sie danach über einer früher abzurufenden Nummer und muss ein zweites Mal bewegt werden. "
           f"LB2 = 3 + 1 = **{hv['LB2']}**; das Optimum ist **{hopt}**. Die einfache Zählung lag um {hopt - hv['LB1']} darunter, LB2 trifft.")
miss_v = A.bound_values(C.MISS_BAY, C.MISS_HEIGHT)
st.markdown(f"**Der eine Fehlschlag von LB2 unter allen 120 Buchten 3 × 2** (bis auf Vertauschen der Stapel): (1, 5), (3, 6), (4, 2), Höchsthöhe 4. LB2 liegt bei {miss_v['LB2']}, "
            f"das Optimum ist {A.search(C.MISS_BAY, C.MISS_HEIGHT).optimum}: Den vierten Hub erzwingt erst ein späterer Abrufschritt. Das Preset „LB2 verfehlt“ lädt diese Bucht (mit vertauschten Stapeln).")

st.markdown("---")

# --- Experiment: wie oft trifft die Schranke -----------------------------------------------------------------------------------------------------

bands = _bands()
zellen = bands["zellen"]
here = zellen.get(cell_key(settings.stacks, settings.layers))
st.subheader("🔬 Experiment: Wie oft trifft die Schranke das Optimum?")
st.caption("Je Zelle feste Buchten (Platz 2, dieselben wie in Stück 4 bis 8), vorberechnet (`generate_precomputed.py`). Optimum aus der Suche; Lücke = Optimum minus Schranke (Mittel / Maximum).")
ta = ["| Zelle (Buchten) | Optimum Mittel | LB1 trifft | LB2 trifft | LB3 trifft | LB4 trifft | Lücke LB1 | Lücke LB2 | Lücke LB4 |", "|---|---|---|---|---|---|---|---|---|"]
for s_, l_, n_ in C.HIT_CELLS:
    c = zellen[cell_key(s_, l_)]
    ta.append(f"| {s_} × {l_} ({c['n']}) | {dec(c['opt_mean'])} | {c['hit']['LB1']} | {c['hit']['LB2']} | {c['hit']['LB3']} | {c['hit']['LB4']} | "
              + " | ".join(f"{dec(c['gap_mean'][k])} / {c['gap_max'][k]}" for k in ("LB1", "LB2", "LB4")) + " |")
st.markdown("\n".join(ta))
st.plotly_chart(build_hits(zellen), width="stretch", key="chart_hits")
st.plotly_chart(build_gap(zellen), width="stretch", key="chart_gap")
st.markdown(f"**Zelle {settings.stacks} × {settings.layers} (Ihre Einstellung)**" + ("" if settings.extra == C.DEFAULT_EXTRA else f", Tabellen gelten für Platz {C.DEFAULT_EXTRA}, hier ist Platz {settings.extra} eingestellt") + ":")
if here is None:
    st.info(f"Für {settings.stacks} × {settings.layers} wurden die Schranken nicht vorberechnet; die Tabelle zeigt die Zellen, die gerechnet wurden.")
else:
    kind, text = verdict_hits(here, f"{settings.stacks} × {settings.layers}")
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: zwei Lagen ------------------------------------------------------------------------------------------------------------------------

zwei = bands["zwei_lagen"]
st.subheader("🔬 Experiment: Zwei Lagen")
st.caption("Bei zwei Lagen liegt über jedem Container höchstens einer. Alle 120 Buchten 3 × 2 (bis auf Vertauschen der Stapel) und Zufallsbuchten mit 4, 5 und 6 Stapeln (Seeds ab 1000): in wie vielen verfehlt die Schranke das Optimum?")
tb = ["| Zelle (Buchten) | LB1 verfehlt | LB2 verfehlt | LB3 verfehlt | LB4 verfehlt |", "|---|---|---|---|---|"]
for key, label in (("alle32", "3 × 2, alle"), (cell_key(4, 2), "4 × 2"), (cell_key(5, 2), "5 × 2"), (cell_key(6, 2), "6 × 2")):
    c = zwei[key]
    tb.append(f"| {label} ({c['n']}) | " + " | ".join(str(c["miss"][k]) for k in A.BOUNDS) + " |")
st.markdown("\n".join(tb))
kind, text = verdict_two(zwei[cell_key(4, 2)], "4 × 2")
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: was hat die Suche davon -----------------------------------------------------------------------------------------------------------

suche = bands["suche"]
st.subheader("🔬 Experiment: Was hat die Suche davon?")
st.caption("IDA* mit Zustandsmerken (Stück 5 und 6), je Bucht mit jeder der vier Schranken; Knotenlimit 1 Million. Knoten Median / Maximum; Zeit Median je Bucht (Einzelmessungen, Python). Alle Läufe finden dasselbe Optimum.")
tc = ["| Zelle (Buchten) | Knoten LB1 | Knoten LB2 | Knoten LB3 | Knoten LB4 | Zeit LB1 | Zeit LB2 | Zeit LB3 | Zeit LB4 |", "|---|---|---|---|---|---|---|---|---|"]
for s_, l_, n_ in C.SEARCH_CELLS:
    c = suche[cell_key(s_, l_)]
    tc.append(f"| {s_} × {l_} ({c['n']}) | " + " | ".join(f"{num_f(c['nodes'][k]['median'])} / {num(c['nodes'][k]['max'])}" for k in A.BOUNDS) + " | "
              + " | ".join(time_text(c["ms"][k]) for k in A.BOUNDS) + " |")
st.markdown("\n".join(tc))
st.plotly_chart(build_nodes(suche), width="stretch", key="chart_nodes")
st.plotly_chart(build_time(suche), width="stretch", key="chart_time")
here_s = suche.get(cell_key(settings.stacks, settings.layers))
if here_s is not None:
    st.markdown(f"**Zelle {settings.stacks} × {settings.layers} (Ihre Einstellung):**")
    kind, text = verdict_search(here_s, f"{settings.stacks} × {settings.layers}")
    getattr(st, kind)(text)
else:
    st.info(f"Für {settings.stacks} × {settings.layers} wurde die Suche nicht vorberechnet (Zellen: 3 × 3, 4 × 3, 5 × 3, 4 × 4, 5 × 4); die Tabelle zeigt sie.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Nur ein Abrufschritt Vorausschau** | LB4 schaut einen Schritt voraus; tiefere Vorausschau (LB5 und weiter) ist nicht gemessen. Die Lücke bleibt bei 3 und 4 Lagen: sie kommt aus späteren Abrufschritten. | – |
| **Zeiten sind Einzelmessungen** | Python, ein Lauf, eine Windows-Maschine; die Aussage „LB3 und LB4 sparen Knoten, aber keine Zeit“ gilt für diese Umsetzung (die Vorausschau ist nicht optimiert). | – |
| **Eigene Konstruktion** | Die Zählung „kein sicherer Stapel“ ist aus dem Gedächtnis dem Stand der Technik zugeordnet (Zhu u. a. 2012), nicht nachgeprüft; LB3 und LB4 sind eigene Bausteine. | – |
| **Nur restricted, nur volle Buchten, Platz 2 in den Tabellen** | Mit anderer Hubmenge (Stück 3), anderer Füllung oder anderem Platz ändern sich die Zahlen. | – |
| **Kleine Zellen** | 5 × 3 mit 60, 4 × 4 mit 60 und 5 × 4 mit 40 Buchten in der Suchtabelle; die Aussagen dort sind grob. | – |
| **Zwei Lagen: Zufallsbuchten** | 4, 5 und 6 Stapel sind je 1 500, 300 und 100 Zufallsbuchten, nicht alle; nur 3 × 2 ist vollständig (120 Buchten). | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben:** Bucht aus Stapeln, Höchsthöhe $H$, Abrufnummern $1, \dots, N$ (kleiner = früher), restricted. Zustand = Bucht nach dem Abruf; nächster Abruf $t$ im Stapel $i$; $B = (c_1, \dots, c_r)$ die Container über $t$ (oben zuerst); $m_k$ die früheste Abrufnummer im Stapel $k$ (leer: $\infty$).

**LB1.** $\text{LB1} = |\{c : c \text{ liegt über einem kleineren im selben Stapel}\}|$. Jeder dieser Container wird mindestens einmal bewegt, und nur solche werden je bewegt (Stück 2).

**LB2.** $\text{LB2} = \text{LB1} + |\{ c \in B : c > \max_{k \ne i} m_k \}|$.

*Beweis.* Jedes $c \in B$ muss auf einen Stapel $k \neq i$ gesetzt werden, bevor $t$ abgerufen wird. Dort liegt schon ein Container mit der Nummer $m_k < c$ (durch Aufsetzen sinkt ein Stapelminimum nur). Nach dem Aufsetzen liegt $c$ also über einem früher abzurufenden Container und muss vor diesem noch einmal bewegt werden. Dieser zweite Hub von $c$ ist verschieden vom ersten Hub von $c$ und von jedem Hub eines anderen Containers; LB1 zählt nur erste Hübe. $\square$

**LB3.** Wie LB2, aber die Platzierungen der $c_1, \dots, c_r$ werden der Reihe nach gewählt (nur Stapel mit Platz); $\text{LB3} = \text{LB1} + \min_{\text{Platzierungen}} |\{ j : \text{Zielstapel von } c_j \text{ enthält zu diesem Zeitpunkt eine kleinere Nummer} \}|$. Jede tatsächliche Folge ist eine der geprüften Platzierungen, jede schlechte Platzierung kostet einen zweiten Hub: zulässig. Jedes $c$ ohne sicheren Stapel ist in jeder Platzierung schlecht: $\text{LB3} \ge \text{LB2}$.

**LB4.** $\text{LB4} = |B| + \min_{\text{Platzierungen}} \text{LB2}(\text{Zustand nach dem Abruf von } t)$. Die Hübe dieser Runde kosten $|B|$, den Rest des Problems mindestens LB2 des Folgezustands (zulässig). LB1 des Folgezustands enthält jeden schlecht platzierten Container, also $\text{LB4} \ge \text{LB3}$.

**Suche.** IDA\* (Stück 5): Budget = Untergrenze der Wurzel, je Budget eine Tiefensuche, Abbruch bei $g + \text{LB} > \text{Budget}$, dazu Zustandsmerken (Stück 6). Eine schärfere Untergrenze verkleinert die Zahl der Knoten, aber nicht die Kosten je Knoten.

**Literatur.** Die Zählung der Container ohne sicheren Stapel steht dem Stand der Technik nahe (IDA\* beim Relocation-Problem, Zhu u. a. 2012, aus dem Gedächtnis, nicht gelesen); die Bausteine hier sind eigene Konstruktionen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
