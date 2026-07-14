import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from matplotlib.patches import FancyBboxPatch

nodos = {
    "N01": {"texto": "Inicio\nSintoma\npredominante?", "nivel": 0, "es_hoja": False},
    "N02": {"texto": "Sintomas fisicos\nAgudo o\ncronico?", "nivel": 1, "es_hoja": False},
    "N03": {"texto": "Sintomas mentales\nBloqueo o\nhiperactividad?", "nivel": 1, "es_hoja": False},
    "N04": {"texto": "Sintomas emocionales\nFrustracion o\ntristeza?", "nivel": 1, "es_hoja": False},
    "N05": {"texto": "Estres Agudo\nEnfoque?", "nivel": 2, "es_hoja": False},
    "N06": {"texto": "Burnout\nNecesitas?", "nivel": 2, "es_hoja": False},
    "N07": {"texto": "Bloqueo Mental\nAbordarlo?", "nivel": 2, "es_hoja": False},
    "N08": {"texto": "Overthinking\nCalmarla?", "nivel": 2, "es_hoja": False},
    "N09": {"texto": "Frustracion\nCanalizarla?", "nivel": 2, "es_hoja": False},
    "N10": {"texto": "Melancolia\nAmbiente?", "nivel": 2, "es_hoja": False},
    "N11": {"texto": "Frecuencia\nSolfeggio?", "nivel": 3, "es_hoja": False},
    "N12": {"texto": "Sonido de\nnaturaleza?", "nivel": 3, "es_hoja": False},
    "N13": {"texto": "Ambiente\nsonoro denso?", "nivel": 3, "es_hoja": False},
    "N14": {"texto": "Activar enfoque\ncon binaurales?", "nivel": 3, "es_hoja": False},
    "N15": {"texto": "Sumergirte en\nLo-Fi Chillhop?", "nivel": 3, "es_hoja": False},
    "N16": {"texto": "Liberar frustracion\ncon Post-Rock?", "nivel": 3, "es_hoja": False},
    "N17": {"texto": "528Hz\nReparacion\ny Sanacion", "nivel": 4, "es_hoja": True, "diag": "Estres Agudo\nAlta Activacion"},
    "N18": {"texto": "432Hz\nCalma\nProfunda", "nivel": 4, "es_hoja": True, "diag": "Estres Agudo\nCalma Profunda"},
    "N19": {"texto": "Lluvia y\nTormenta\nDormir", "nivel": 4, "es_hoja": True, "diag": "Crisis de\nAnsiedad"},
    "N20": {"texto": "Ruido\nMarron\nProfundo", "nivel": 4, "es_hoja": True, "diag": "Ansiedad\nAguda"},
    "N21": {"texto": "Dark\nAmbient\nEspacial", "nivel": 4, "es_hoja": True, "diag": "Agotamiento\nCronico"},
    "N22": {"texto": "Deep Sleep\nSpace\nMusic", "nivel": 4, "es_hoja": True, "diag": "Insomnio\nCronico"},
    "N23": {"texto": "Ondas Alpha\nEnfoque", "nivel": 4, "es_hoja": True, "diag": "Bloqueo\nCognitivo"},
    "N24": {"texto": "Lo-Fi Beats\nsin Letra", "nivel": 4, "es_hoja": True, "diag": "Ansiedad\nCognitiva"},
    "N25": {"texto": "Post-Rock\nCatartico", "nivel": 4, "es_hoja": True, "diag": "Frustracion\nAcumulada"},
    "N28": {"texto": "Lo-Fi Foco\nCreativo", "nivel": 4, "es_hoja": True, "diag": "Bloqueo\nFlujo Creativo"},
    "N29": {"texto": "Frecuencias\nCalmantes\n432Hz", "nivel": 4, "es_hoja": True, "diag": "Hiperactividad\nMental"},
    "N30": {"texto": "Frecuencias\nde Reparacion\nEnergetica", "nivel": 4, "es_hoja": True, "diag": "Fatiga\nCronica"},
    "N31": {"texto": "Epica\nInstrumental\nLiberadora", "nivel": 4, "es_hoja": True, "diag": "Liberacion\nde Tension"},
}

aristas = [
    ("N01", "N02", "Fisicos"),
    ("N01", "N03", "Mentales"),
    ("N01", "N04", "Emocionales"),
    ("N02", "N05", "Agudo"),
    ("N02", "N06", "Cronico"),
    ("N03", "N07", "Bloqueo"),
    ("N03", "N08", "Hiperactividad"),
    ("N04", "N09", "Frustracion"),
    ("N04", "N10", "Tristeza"),
    ("N05", "N11", "Frecuencias"),
    ("N05", "N12", "Distraccion"),
    ("N06", "N13", "Sueno"),
    ("N06", "N30", "Energia"),
    ("N07", "N14", "Binaurales"),
    ("N07", "N28", "Lo-Fi"),
    ("N08", "N15", "Lo-Fi"),
    ("N08", "N29", "432Hz"),
    ("N09", "N16", "Post-Rock"),
    ("N09", "N31", "Epica"),
    ("N10", "N13", "Ambientes"),
    ("N10", "N15", "Ritmos"),
    ("N11", "N17", "528Hz"),
    ("N11", "N18", "432Hz"),
    ("N12", "N19", "Lluvia"),
    ("N12", "N20", "R. marron"),
    ("N13", "N21", "D. Ambient"),
    ("N13", "N22", "D. Sleep"),
    ("N14", "N23", "Activar"),
    ("N15", "N24", "Lo-Fi"),
    ("N16", "N25", "Catarsis"),
]

COLORES_NIVEL = {
    0: "#1A237E",
    1: "#283593",
    2: "#3949AB",
    3: "#5C6BC0",
    4: "#7986CB",
}
COLOR_HOJA = "#2E7D32"
COLOR_ARISTA = "#78909C"
COLOR_LABEL = "#37474F"

G = nx.DiGraph()
for nid, info in nodos.items():
    G.add_node(nid, **info)
for src, dst, label in aristas:
    G.add_edge(src, dst, label=label)

fig, ax = plt.subplots(1, 1, figsize=(30, 22))
ax.set_facecolor("#FAFAFA")
fig.patch.set_facecolor("#FAFAFA")

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
    try:
        pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
    except Exception:
        pos = nx.spring_layout(G, k=2.0, iterations=200, seed=42)

for node_id, (x, y) in pos.items():
    info = nodos[node_id]
    es_hoja = info["es_hoja"]
    nivel = info["nivel"]
    color = COLOR_HOJA if es_hoja else COLORES_NIVEL.get(nivel, "#9FA8DA")
    text_color = "white"
    font_size = 7.5 if es_hoja else 7

    box = FancyBboxPatch(
        (x - 0.25, y - 0.18), 0.50, 0.36,
        boxstyle="round,pad=0.25",
        facecolor=color, edgecolor=color, alpha=0.92,
        linewidth=1.0,
    )
    ax.add_patch(box)

    ax.text(x, y, info["texto"], ha='center', va='center',
            fontsize=font_size, color=text_color, fontweight='bold',
            fontfamily='sans-serif')

    if es_hoja and info.get("diag"):
        ax.annotate(
            info["diag"], xy=(x, y - 0.25),
            fontsize=6, fontstyle='italic',
            color="#1B5E20",
            ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#E8F5E9",
                      edgecolor="#A5D6A7", alpha=0.85)
        )

# Draw edges with STRAIGHT arrows (no arc)
for src, dst, label in aristas:
    nx.draw_networkx_edges(
        G, pos, edgelist=[(src, dst)],
        arrows=True, arrowstyle='->', arrowsize=14,
        edge_color=COLOR_ARISTA, width=1.5, alpha=0.75,
        connectionstyle='arc3,rad=0',
    )
    x_src, y_src = pos[src]
    x_dst, y_dst = pos[dst]
    x_mid = (x_src + x_dst) / 2
    y_mid = (y_src + y_dst) / 2
    dx = x_dst - x_src
    dy = y_dst - y_src
    offset_x = -dy * 0.04
    offset_y = dx * 0.04
    ax.text(
        x_mid + offset_x, y_mid + offset_y, label,
        fontsize=7.5, color=COLOR_LABEL,
        ha='center', va='bottom',
        style='italic',
        weight='bold',
        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                  edgecolor="#CFD8DC", alpha=0.90)
    )

legend_elements = [
    mpatches.Patch(color=COLORES_NIVEL[0], label="Nivel 0: Raiz"),
    mpatches.Patch(color=COLORES_NIVEL[1], label="Nivel 1: Tipo de sintoma"),
    mpatches.Patch(color=COLORES_NIVEL[2], label="Nivel 2: Clasificacion"),
    mpatches.Patch(color=COLORES_NIVEL[3], label="Nivel 3: Enfoque terapeutico"),
    mpatches.Patch(color=COLORES_NIVEL[4], label="Nivel 4: Intervencion"),
    mpatches.Patch(color=COLOR_HOJA, label="Hoja: Diagnostico + Playlist"),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=9, framealpha=0.9,
          title="Niveles del Arbol", title_fontsize=10)

ax.set_title(
    "Arbol de Decision — Chatbot SBC Musicoterapia (29 Nodos)",
    fontsize=18, fontweight='bold', color="#1A237E", pad=25,
)
ax.text(0.5, -0.03, "Cada hoja (verde) representa un diagnostico unico + playlist de Spotify recomendada",
        transform=ax.transAxes, ha='center', fontsize=10, color="#546E7A", style='italic')
ax.axis('off')
plt.tight_layout()
plt.savefig("docs/arbol_decision.png", dpi=250, bbox_inches='tight', facecolor='#FAFAFA')
plt.close()
print("OK: docs/arbol_decision.png generado")
