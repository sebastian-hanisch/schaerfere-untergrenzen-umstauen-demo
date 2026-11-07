"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sgu_algorithm as A
import sgu_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def blocker_cells(stacks) -> set:
    """Container, die über einem früher abzurufenden im selben Stapel liegen (Position (Stapel, Lage))."""
    out = set()
    for i, s in enumerate(stacks):
        lowest = A.INF
        for j, c in enumerate(s):
            if c > lowest:
                out.add((i, j))
            else:
                lowest = c
    return out


def build_bay(stacks, height, target=None):
    """Die Bucht als Säulen: je Lage ein Balken mit der Abrufnummer. Rot: blockiert einen früher abzurufenden, grün: nächster Abruf
    (`target`, eine Abrufnummer oder None), grau-blau: übrige."""
    blockers = blocker_cells(stacks)
    fig = go.Figure()
    xs = list(range(len(stacks)))
    for j in range(height):
        ys, colors, texts = [], [], []
        for i, s in enumerate(stacks):
            if j < len(s):
                c = s[j]
                ys.append(1)
                texts.append(str(c))
                colors.append(C.COLOR_TARGET if c == target else C.COLOR_BLOCK if (i, j) in blockers else C.COLOR_CELL)
            else:
                ys.append(0)
                texts.append("")
                colors.append(C.COLOR_CELL)
        fig.add_trace(go.Bar(x=xs, y=ys, base=j, marker_color=colors, text=texts, textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#ffffff", size=16), width=0.78, showlegend=False,
                             hovertemplate="Abruf %{text}<extra></extra>", marker_line=dict(width=0)))
    fig.update_layout(barmode="overlay")
    fig.add_hline(y=height, line_dash="dot", line_color="rgba(128,128,128,0.7)", annotation_text="Höchsthöhe", annotation_position="top left")
    fig.update_xaxes(tickvals=xs, ticktext=[f"Stapel {i + 1}" for i in xs], showgrid=False)
    fig.update_yaxes(range=[0, height + 0.35], showticklabels=False, showgrid=False, zeroline=False)
    return _base(fig, height=48 * height + 90)


def _cells_in_order(cells):
    return sorted(cells, key=lambda n: (int(n.split(",")[0]) * int(n.split(",")[1]), n))


def _label(key):
    s, l = key.split(",")
    return f"{s} × {l}"


def build_hits(cells):
    """Anteil der Buchten, in denen die Schranke das Optimum trifft (Prozent), je Zelle und Schranke. `cells`: {"s,l": cell_stats}."""
    keys = _cells_in_order(cells)
    fig = go.Figure()
    for k in A.BOUNDS:
        fig.add_trace(go.Bar(x=[_label(c) for c in keys], y=[100.0 * cells[c]["hit"][k] / cells[c]["n"] for c in keys], name=k, marker_color=C.COLOR_LINES[k],
                             hovertemplate="%{x}: %{y:.0f} %<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle (Stapel × Lagen)")
    fig.update_yaxes(title_text="Anteil der Buchten mit Schranke = Optimum (%)", range=[0, 105])
    return _base(fig, height=360)


def build_gap(cells):
    """Mittlere Lücke (Optimum minus Schranke) je Zelle und Schranke. `cells`: {"s,l": cell_stats}."""
    keys = _cells_in_order(cells)
    fig = go.Figure()
    for k in A.BOUNDS:
        fig.add_trace(go.Bar(x=[_label(c) for c in keys], y=[cells[c]["gap_mean"][k] for c in keys], name=k, marker_color=C.COLOR_LINES[k],
                             hovertemplate="%{x}: %{y:.2f}<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle (Stapel × Lagen)")
    fig.update_yaxes(title_text="mittlere Lücke zum Optimum (Hübe)", rangemode="tozero")
    return _base(fig, height=340)


def build_nodes(cells):
    """Knoten der Suche (Median) je Zelle und Schranke (logarithmisch). `cells`: {"s,l": search_stats}."""
    keys = _cells_in_order(cells)
    fig = go.Figure()
    for k in A.BOUNDS:
        fig.add_trace(go.Bar(x=[_label(c) for c in keys], y=[cells[c]["nodes"][k]["median"] for c in keys], name=k, marker_color=C.COLOR_LINES[k],
                             hovertemplate="%{x}: %{y:,.0f}<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle (Stapel × Lagen)")
    fig.update_yaxes(title_text="Knoten, Median (logarithmisch)", type="log")
    return _base(fig, height=340)


def build_time(cells):
    """Zeit der Suche (Median je Bucht, Millisekunden) je Zelle und Schranke (logarithmisch). `cells`: {"s,l": search_stats}."""
    keys = _cells_in_order(cells)
    fig = go.Figure()
    for k in A.BOUNDS:
        fig.add_trace(go.Bar(x=[_label(c) for c in keys], y=[cells[c]["ms"][k] for c in keys], name=k, marker_color=C.COLOR_LINES[k],
                             hovertemplate="%{x}: %{y:,.1f} ms<extra>%{fullData.name}</extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category", title_text="Zelle (Stapel × Lagen)")
    fig.update_yaxes(title_text="Zeit je Bucht, Median (ms, logarithmisch)", type="log")
    return _base(fig, height=340)
