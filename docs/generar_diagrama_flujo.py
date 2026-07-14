import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(1, 1, figsize=(16, 14))
ax.set_xlim(0, 16)
ax.set_ylim(0, 14)
ax.axis('off')
ax.set_facecolor("#FAFAFA")
fig.patch.set_facecolor("#FAFAFA")

COLOR_START = "#1A237E"
COLOR_PROCESS = "#3949AB"
COLOR_DECISION = "#C62828"
COLOR_RESULT = "#2E7D32"
COLOR_SPOTIFY = "#1DB954"
COLOR_EMPATHY = "#D4933A"
COLOR_ARROW = "#546E7A"
COLOR_LABEL = "#37474F"


def draw_box(ax, x, y, w, h, text, color, text_color="white", fontsize=9, alpha=0.92):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.3",
        facecolor=color, edgecolor=color, alpha=alpha,
        linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=text_color, fontfamily='sans-serif')


def draw_diamond(ax, x, y, w, h, text, color="#C62828", text_color="white", fontsize=8):
    diamond = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor=color, alpha=0.90,
        linewidth=1.2,
    )
    ax.add_patch(diamond)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color=text_color, fontfamily='sans-serif')


def arrow_straight(ax, x1, y1, x2, y2, label="", color=COLOR_ARROW, lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw, connectionstyle='arc3,rad=0'))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.15, my - 0.2, label, ha='center', va='top',
                fontsize=7.5, color=COLOR_LABEL, style='italic',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='#CFD8DC', alpha=0.9))


def arrow_simple(ax, x1, y1, x2, y2, color=COLOR_ARROW):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5, connectionstyle='arc3,rad=0'))


# Title
ax.text(8, 13.5, "Diagrama de Flujo — Motor FSM del Chatbot SBC Musicoterapia",
        ha='center', va='center', fontsize=15, fontweight='bold',
        color="#1A237E", fontfamily='sans-serif')

# ===== ROW 1: INICIO =====
draw_box(ax, 8, 12.2, 3.5, 0.75, "INICIO\nUsuario abre la aplicacion", COLOR_START, fontsize=10)
arrow_straight(ax, 8, 11.8, 8, 11.0)

# ===== ROW 2: BIENVENIDA =====
draw_box(ax, 8, 10.5, 3.5, 0.75, "Mostrar mensaje de bienvenida\ny pregunta con opciones", COLOR_PROCESS, fontsize=9)
arrow_straight(ax, 8, 10.1, 8, 9.3)

# ===== ROW 3: DECISION - Opcion o texto? =====
draw_diamond(ax, 8, 8.7, 3.0, 1.0, "Usuario elige\nopcion o\nescribe texto?", COLOR_DECISION, fontsize=8)

# Izquierda: texto libre
arrow_straight(ax, 6.5, 8.4, 2.2, 7.5)
# Derecha: opcion
arrow_straight(ax, 9.5, 8.4, 13.8, 7.5)

# ===== RAMA IZQUIERDA: Procesar texto =====
draw_box(ax, 2.2, 7.0, 2.6, 0.7, "Detectar emocion\n(emociones.py)", COLOR_PROCESS, fontsize=9)
arrow_simple(ax, 2.2, 6.6, 2.2, 5.9)

draw_box(ax, 2.2, 5.4, 2.6, 0.7, "Coincidir intencion\n(intenciones.py)", COLOR_PROCESS, fontsize=9)
arrow_straight(ax, 2.2, 5.0, 3.8, 3.8)

# ===== RAMA DERECHA: Opcion =====
draw_box(ax, 13.8, 7.0, 2.6, 0.7, "Obtener nodo\ndestino de la opcion", COLOR_PROCESS, fontsize=9)
arrow_simple(ax, 13.8, 6.6, 12.0, 5.2)

# ===== DECISION: Coincide intencion? =====
draw_diamond(ax, 3.8, 3.3, 2.4, 0.85, "Coincide con\nopcion\ndisponible?", COLOR_DECISION, fontsize=7)

# No match
arrow_straight(ax, 2.8, 3.0, 0.6, 1.6, "No", COLOR_DECISION)
draw_box(ax, 0.8, 1.1, 2.0, 0.7, "Mostrar mensaje\nempatico + repetir", COLOR_EMPATHY, fontsize=8)
arrow_straight(ax, 1.6, 0.7, 4.0, 0.7)

# Si match
arrow_straight(ax, 4.5, 2.8, 5.8, 1.8, "Si", COLOR_RESULT)

# ===== DECISION: Emocion esperada? =====
draw_diamond(ax, 8.0, 3.3, 2.6, 1.0, "Emocion detectada\ncoincide con\nla esperada?", COLOR_DECISION, fontsize=8)

# No - redirigir
arrow_straight(ax, 6.5, 3.0, 4.0, 1.8, "No\n(redirigir)", COLOR_EMPATHY)
draw_box(ax, 4.0, 1.3, 2.2, 0.65, "Sugerir rama\nalternativa", COLOR_EMPATHY, fontsize=8)

# Si - continuar
arrow_straight(ax, 9.2, 2.8, 11.5, 1.8, "Si", COLOR_RESULT)

# ===== TRANSICION =====
arrow_simple(ax, 4.0, 0.9, 8.0, 0.9)
arrow_simple(ax, 5.8, 1.4, 8.0, 1.4)
arrow_simple(ax, 9.5, 1.7, 11.5, 1.7)
arrow_simple(ax, 11.5, 0.8, 12.2, 0.8)

draw_box(ax, 8.0, 0.45, 2.4, 0.6, "Transicionar al\nnodo destino", COLOR_PROCESS, fontsize=9)

arrow_simple(ax, 11.5, 0.8, 12.2, 0.8)
arrow_simple(ax, 8.0, 0.8, 8.0, 1.2)
arrow_simple(ax, 4.0, 0.9, 8.0, 0.9)

# ===== Bottom section =====
# From Transition, go down to check if leaf
arrow_straight(ax, 8.0, 0.05, 13.5, -0.5)

# ===== LEGEND =====
legend_elements = [
    mpatches.Patch(color=COLOR_START, label="Inicio"),
    mpatches.Patch(color=COLOR_PROCESS, label="Proceso / Accion"),
    mpatches.Patch(color=COLOR_DECISION, label="Decision (si/no)"),
    mpatches.Patch(color=COLOR_RESULT, label="Diagnostico / Resultado"),
    mpatches.Patch(color=COLOR_SPOTIFY, label="Integracion Spotify"),
    mpatches.Patch(color=COLOR_EMPATHY, label="Redireccion emocional"),
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=7.5, framealpha=0.9,
          title="Leyenda", title_fontsize=8, bbox_to_anchor=(0.99, 0.24))

# ===== SIDE PANEL: Post-transition flow =====
y_base = -0.5

# Decision: hoja?
draw_diamond(ax, 13.5, y_base, 2.2, 0.8, "Es nodo\nhoja?", COLOR_DECISION, fontsize=7)

# No -> continuar
arrow_straight(ax, 12.5, y_base - 0.3, 10.0, -2.0, "No", COLOR_ARROW)
draw_box(ax, 10.0, -2.5, 2.4, 0.7, "Continuar dialogo:\nmostrar nueva pregunta", COLOR_PROCESS, fontsize=8)

# Si -> diagnostico
arrow_straight(ax, 14.3, y_base - 0.1, 14.3, -1.6, "Si", COLOR_RESULT)
draw_box(ax, 14.3, -2.1, 2.6, 0.7, "Mostrar diagnostico:\ntitulo + recomendacion", COLOR_RESULT, fontsize=8)

arrow_simple(ax, 14.3, -2.5, 14.3, -3.2)
draw_box(ax, 14.3, -3.7, 2.6, 0.7, "Buscar playlist en\nSpotify (spotify.py)", COLOR_SPOTIFY, fontsize=8)

arrow_simple(ax, 14.3, -4.05, 14.3, -4.7)
draw_box(ax, 14.3, -5.2, 2.8, 0.8, "Mostrar resultado:\nAbrir / Reproducir\nNuevo diagnostico", COLOR_SPOTIFY, fontsize=8)

ax.set_ylim(-6.0, 14.0)

# Return arrow from "continuar" back to top
ax.annotate('', xy=(8.0, 10.1), xytext=(9.0, -2.1),
            arrowprops=dict(arrowstyle='->', color=COLOR_ARROW, lw=1.5,
                          linestyle='dashed', connectionstyle='arc3,rad=0'))
ax.text(8.5, 4.0, "Bucle de\ndialogo", ha='center', va='center',
        fontsize=7, color=COLOR_LABEL, style='italic',
        bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='#CFD8DC', alpha=0.9))

plt.tight_layout()
plt.savefig("docs/diagrama_flujo_fsm.png", dpi=200, bbox_inches='tight', facecolor='#FAFAFA')
plt.close()
print("OK: docs/diagrama_flujo_fsm.png generado")
