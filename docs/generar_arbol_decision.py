import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from matplotlib.patches import FancyBboxPatch

nodros = {
    "N01": {"texto": "¿Cuál es el síntoma\npredominante?", "nivel": 0, "es_hoja": False},
    "N02": {"texto": "Síntomas físicos\n¿Agudo o crónico?", "nivel": 1, "es_hoja": False},
    "N03": {"texto": "Síntomas mentales\n¿Bloqueo o\nhiperactividad?", "nivel": 1, "es_hoja": False},
    "N04": {"texto": "Síntomas emocionales\n¿Frustración o\ntristeza?", "nivel": 1, "es_hoja": False},
    "N05": {"texto": "Estrés Agudo\n¿Qué enfoque?", "nivel": 2, "es_hoja": False},
    "N06": {"texto": "Burnout\n¿Qué necesitas?", "nivel": 2, "es_hoja": False},
    "N07": {"texto": "Bloqueo Mental\n¿Cómo abordarlo?", "nivel": 2, "es_hoja": False},
    "N08": {"texto": "Overthinking\n¿Cómo calmarla?", "nivel": 2, "es_hoja": False},
    "N09": {"texto": "Frustración\n¿Cómo canalizarla?", "nivel": 2, "es_hoja": False},
    "N10": {"texto": "Melancolía\n¿Qué ambiente?", "nivel": 2, "es_hoja": False},
    "N11": {"texto": "¿Qué frecuencia\nSolfeggio?", "nivel": 3, "es_hoja": False},
    "N12": {"texto": "¿Qué sonido de\nla naturaleza?", "nivel": 3, "es_hoja": False},
    "N13": {"texto": "¿Qué ambiente\nsonoro denso?", "nivel": 3, "es_hoja": False},
    "N14": {"texto": "¿Activar enfoque\ncon binaurales?", "nivel": 3, "es_hoja": False},
    "N15": {"texto": "¿Sumergirte en\nLo-Fi Chillhop?", "nivel": 3, "es_hoja": False},
    "N16": {"texto": "¿Liberar\nfrustración\ncon Post-Rock?", "nivel": 3, "es_hoja": False},
    "N17": {"texto": "528Hz Reparación\ny Sanación", "nivel": 4, "es_hoja": True, "diag": "Estrés Agudo con\nAlta Activación"},
    "N18": {"texto": "432Hz Calma\nProfunda", "nivel": 4, "es_hoja": True, "diag": "Estrés Agudo con\nNecesidad de Calma"},
    "N19": {"texto": "Lluvia y Tormenta\npara Dormir", "nivel": 4, "es_hoja": True, "diag": "Crisis de Ansiedad\ncon Escudo Acústico"},
    "N20": {"texto": "Ruido Marrón\nProfundo", "nivel": 4, "es_hoja": True, "diag": "Ansiedad Aguda con\nRuido Mental"},
    "N21": {"texto": "Dark Ambient\nEspacial", "nivel": 4, "es_hoja": True, "diag": "Agotamiento Crónico\nDesconexión Profunda"},
    "N22": {"texto": "Deep Sleep\nSpace Music", "nivel": 4, "es_hoja": True, "diag": "Insomnio por Estrés\nCrónico"},
    "N23": {"texto": "Ondas Alpha\npara Enfoque", "nivel": 4, "es_hoja": True, "diag": "Bloqueo Mental por\nSobrecarga Cognitiva"},
    "N24": {"texto": "Lo-Fi Beats\nsin Letra", "nivel": 4, "es_hoja": True, "diag": "Ansiedad Cognitiva\nHiperactividad Mental"},
    "N25": {"texto": "Post-Rock\nInstrumental\nCatártico", "nivel": 4, "es_hoja": True, "diag": "Frustración Acumulada\nCatarsis Emocional"},
    "N28": {"texto": "Lo-Fi Foco\nCreativo", "nivel": 4, "es_hoja": True, "diag": "Bloqueo Mental\nFlujo Creativo"},
    "N29": {"texto": "Frecuencias\nCalmantes 432Hz", "nivel": 4, "es_hoja": True, "diag": "Hiperactividad Mental\nCalma y Silencio"},
    "N30": {"texto": "Frecuencias de\nReparación\nEnergética", "nivel": 4, "es_hoja": True, "diag": "Fatiga Crónica\nReparación Energética"},
    "N31": {"texto": "Épica\nInstrumental\nLiberadora", "nivel": 4, "es_hoja": True, "diag": "Frustración\nLiberación de Tensión"},
}

aristas = [
    ("N01", "N02", "Síntomas físicos"),
    ("N01", "N03", "Síntomas mentales"),
    ("N01", "N04", "Síntomas emocionales"),
    ("N02", "N05", "Agudo"),
    ("N02", "N06", "Crónico"),
    ("N03", "N07", "Bloqueo"),
    ("N03", "N08", "Hiperactividad"),
    ("N04", "N09", "Frustración"),
    ("N04", "N10", "Tristeza"),
    ("N05", "N11", "Frecuencias"),
    ("N05", "N12", "Distracción"),
    ("N06", "N13", "Conciliar sueño"),
    ("N06", "N30", "Recuperar energía"),
    ("N07", "N14", "Binaurales"),
    ("N07", "N28", "Lo-Fi enfoque"),
    ("N08", "N15", "Lo-Fi suave"),
    ("N08", "N29", "Frecuencias tranquilas"),
    ("N09", "N16", "Post-Rock"),
    ("N09", "N31", "Épica instrumental"),
    ("N10", "N13", "Ambientes densos"),
    ("N10", "N15", "Ritmos suaves"),
    ("N11", "N17", "528Hz"),
    ("N11", "N18", "432Hz"),
    ("N12", "N19", "Lluvia"),
    ("N12", "N20", "Ruido marrón"),
    ("N13", "N21", "Dark Ambient"),
    ("N13", "N22", "Deep Sleep"),
    ("N14", "N23", "Sí, activar"),
    ("N15", "N24", "Sí, Lo-Fi"),
    ("N16", "N25", "Sí, catarsis"),
]

G = nx.DiGraph()
for nid, info in nodros.items():
    G.add_node(nid, **info)
for src, dst, label in aristas:
    G.add_edge(src, dst, label=label)

colores_nivel = {
    0: "#1a237e",
    1: "#283593",
    2: "#3949ab",
    3: "#5c6bc0",
    4: "#7986cb",
}
color_hoja = "#2e7d32"

fig, ax = plt.subplots(1, 1, figsize=(28, 20))
pos = None
try:
    import pydot
    pos = nx.nx_pydot.pydot_layout(G, prog="dot")
except Exception:
    try:
        import pygraphviz
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    except Exception:
        pass

if pos is None:
    print("ADVERTENCIA: graphviz no disponible, usando spring_layout (puede tardar)")
    pos = nx.spring_layout(G, k=1.8, iterations=200, seed=42)

ax.set_facecolor("#fafafa")
fig.patch.set_facecolor("#fafafa")

for node_id, (x, y) in pos.items():
    info = nodros[node_id]
    es_hoja = info["es_hoja"]
    nivel = info["nivel"]
    color = color_hoja if es_hoja else colores_nivel.get(nivel, "#9fa8da")
    text_color = "white"
    box_style = "round,pad=0.4" if not es_hoja else "round,pad=0.5"

    bbox_props = dict(boxstyle=box_style, facecolor=color, edgecolor=color, alpha=0.9)
    nx.draw_networkx_nodes(G, pos, nodelist=[node_id], node_size=1, node_color=color)
    nx.draw_networkx_labels(
        G, pos, labels={node_id: info["texto"]},
        font_size=7, font_color=text_color, font_weight='bold',
        bbox=bbox_props, ax=ax
    )

    if es_hoja:
        diag = info.get("diag", "")
        if diag:
            ax.annotate(
                diag, xy=(x, y - 0.5),
                fontsize=5.5, fontstyle='italic',
                color="#1b5e20",
                ha='center', va='top',
                bbox=dict(boxstyle="round,pad=0.15", facecolor="#e8f5e9", edgecolor="#a5d6a7", alpha=0.8)
            )

for src, dst, label in aristas:
    color_arista = "#78909c"
    nx.draw_networkx_edges(
        G, pos, edgelist=[(src, dst)],
        arrows=True, arrowstyle='->', arrowsize=12,
        edge_color=color_arista, width=1.2, alpha=0.7,
        connectionstyle='arc3,rad=0.05'
    )
    x_src, y_src = pos[src]
    x_dst, y_dst = pos[dst]
    x_mid = (x_src + x_dst) / 2
    y_mid = (y_src + y_dst) / 2
    dx = x_dst - x_src
    dy = y_dst - y_src
    offset_x = -dy * 0.03
    offset_y = dx * 0.03
    ax.text(
        x_mid + offset_x, y_mid + offset_y, label,
        fontsize=5.5, color="#37474f",
        ha='center', va='bottom',
        style='italic',
        bbox=dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="#cfd8dc", alpha=0.85)
    )

leyenda_handles = [
    mpatches.Patch(color=colores_nivel[0], label="Nivel 0: Raíz"),
    mpatches.Patch(color=colores_nivel[1], label="Nivel 1: Tipo de síntoma"),
    mpatches.Patch(color=colores_nivel[2], label="Nivel 2: Clasificación"),
    mpatches.Patch(color=colores_nivel[3], label="Nivel 3: Enfoque terapéutico"),
    mpatches.Patch(color=colores_nivel[4], label="Nivel 4: Intervención"),
    mpatches.Patch(color=color_hoja, label="Hoja: Diagnóstico + Playlist"),
]
ax.legend(handles=leyenda_handles, loc='lower left', fontsize=8, framealpha=0.9,
          title="Niveles del Árbol", title_fontsize=9)

ax.set_title(
    "Árbol de Decisión - Chatbot SBC Musicoterapia (29 Nodos)",
    fontsize=16, fontweight='bold', color="#1a237e", pad=20
)
ax.text(0.5, -0.03, "Cada hoja (verde) representa un diagnóstico + playlist de Spotify recomendada",
        transform=ax.transAxes, ha='center', fontsize=9, color="#546e7a", style='italic')
ax.axis('off')
plt.tight_layout()
plt.savefig("docs/arbol_decision.png", dpi=200, bbox_inches='tight', facecolor='#fafafa')
plt.close()
print("OK: docs/arbol_decision.png generado")
