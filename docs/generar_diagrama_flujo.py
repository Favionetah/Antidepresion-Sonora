import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(14, 16))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')
ax.set_facecolor("#fafafa")
fig.patch.set_facecolor("#fafafa")

def caja(x, y, ancho, alto, texto, color="#3949ab", texto_color="white", tam=10):
    estilo = dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor=color, alpha=0.9)
    ax.text(x, y, texto, ha='center', va='center', fontsize=tam,
            fontweight='bold', color=texto_color, bbox=estilo,
            transform=ax.transData, fontfamily='sans-serif')

def diamante(x, y, texto, color="#e94560", tam=9):
    ax.plot(x, y, marker='D', markersize=55, color=color, alpha=0.85, transform=ax.transData)
    ax.text(x, y, texto, ha='center', va='center', fontsize=tam,
            fontweight='bold', color='white', transform=ax.transData)

def flecha(x1, y1, x2, y2, texto="", color="#78909c"):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5, connectionstyle='arc3,rad=0.05'),
                transform=ax.transData)
    if texto:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.1, my + 0.15, texto, ha='center', va='bottom',
                fontsize=8, color="#37474f", style='italic', transform=ax.transData)

# Nodos del diagrama de flujo
caja(5, 11.5, 3, 0.7, "INICIO\nUsuario abre la aplicación", "#1a237e", tam=11)
flecha(5, 10.8, 5, 10.0)

caja(5, 9.5, 3.2, 0.8, "Mostrar mensaje de bienvenida\ny pregunta con opciones", "#283593", tam=10)
flecha(5, 9.0, 5, 8.2)

diamante(5, 7.5, "¿Usuario\nelige opción\no escribe texto?", "#e94560", tam=8)
flecha(2.5, 7.5, 1.5, 6.5, "Escribe texto")
flecha(7.5, 7.5, 8.5, 6.5, "Elige opción")

# Rama izquierda: texto libre
caja(1.5, 5.8, 2.5, 0.7, "Detectar emoción\n(emociones.py)", "#5c6bc0", tam=9)
flecha(1.5, 5.1, 1.5, 4.3)

caja(1.5, 3.6, 2.5, 0.7, "Coincidir intención\n(intenciones.py)", "#5c6bc0", tam=9)
flecha(1.5, 2.9, 2.5, 2.1)

diamante(2.5, 1.5, "¿Coincide\ncon opción\ndisponible?", "#e94560", tam=7)
flecha(0.5, 1.5, 0.5, 0.5, "No", "#c62828")
caja(0.5, 0.0, 2, 0.6, "Mostrar mensaje\nempático + repetir", "#c62828", tam=8, texto_color="white")
flecha(2.5, 0.8, 3.5, 0.8, "Sí", "#2e7d32")

# Rama derecha: opción clickeada
caja(8.5, 5.8, 2.5, 0.7, "Obtener nodo\ndestino de la opción", "#5c6bc0", tam=9)
flecha(8.5, 5.1, 7.0, 4.3)

# Unión
diamante(5, 3.0, "¿Emoción detectada\ncoincide con\nesperada?", "#e94560", tam=7)
flecha(3.5, 2.5, 3.0, 1.6, "No (redirigir)")
caja(3.0, 1.0, 2.2, 0.6, "Sugerir rama\nalternativa", "#ff8f00", tam=8)
flecha(7.0, 3.0, 7.0, 2.1, "Sí", "#2e7d32")

# Transición
caja(5, 2.1, 2, 0.6, "Transicionar\nal nodo destino", "#3949ab", tam=9)
flecha(5, 1.6, 5, 0.8)

# Verificar hoja
diamante(5, 0.2, "¿Es nodo\nhoja?", "#e94560", tam=8)
flecha(3.5, -0.5, 1.5, -1.5, "No", "#c62828")
caja(1.5, -2.0, 2.5, 0.8, "Continuar diálogo:\nmostrar nueva pregunta", "#3989ab", tam=9)
flecha(3.0, -1.5, 4.0, -1.5, "", "#78909c")

flecha(7.0, -0.5, 9.0, -1.5, "Sí", "#2e7d32")
caja(9.0, -2.0, 2.8, 0.8, "Mostrar diagnóstico:\ntítulo + recomendación", "#2e7d32", tam=9)
flecha(9.0, -2.5, 9.0, -3.5)

caja(9.0, -4.0, 2.8, 0.8, "Buscar playlist en\nSpotify (spotify.py)", "#1DB954", tam=9)
flecha(9.0, -4.5, 9.0, -5.5)

caja(9.0, -6.0, 2.8, 0.8, "Mostrar resultado:\nAbrir/Reproducir\nNuevo diagnóstico", "#1DB954", tam=8)

# Título
ax.set_title("Diagrama de Flujo - Motor FSM del Chatbot SBC", fontsize=14,
             fontweight='bold', color="#1a237e", pad=20)

# Leyenda
leyenda = [
    mpatches.Patch(color="#3949ab", label="Proceso/Acción"),
    mpatches.Patch(color="#e94560", label="Decisión (sí/no)"),
    mpatches.Patch(color="#2e7d32", label="Diagnóstico/Resultado"),
    mpatches.Patch(color="#1DB954", label="Integración Spotify"),
    mpatches.Patch(color="#ff8f00", label="Redirección emocional"),
]
ax.legend(handles=leyenda, loc='lower center', bbox_to_anchor=(0.5, -0.08),
          ncol=5, fontsize=8, framealpha=0.9)

ax.set_ylim(-6.5, 12.5)
plt.tight_layout()
plt.savefig("docs/diagrama_flujo_fsm.png", dpi=200, bbox_inches='tight', facecolor='#fafafa')
plt.close()
print("OK: docs/diagrama_flujo_fsm.png generado")
