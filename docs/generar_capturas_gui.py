from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ANCHO = 520
ALTO = 720
FONDO = "#1a1a2e"
CARD = "#16213e"
PRIMARY = "#0f3460"
ACCENT = "#e94560"
TEXTO_CLARO = "#e0e0e0"
TEXTO_OSCURO = "#1a1a2e"
BURBUJA_BOT = "#2a2a5e"
BURBUJA_USER = "#0f3460"
VERDE_SPOTIFY = "#1DB954"
BLANCO = "#FFFFFF"

OUT_DIR = "docs"

def redondear(imagen, radio):
    mascara = Image.new("L", imagen.size, 0)
    draw = ImageDraw.Draw(mascara)
    draw.rounded_rectangle((0, 0, imagen.size[0], imagen.size[1]), radius=radio, fill=255)
    imagen.putalpha(mascara)
    return imagen

def fuente(tam):
    try:
        return ImageFont.truetype("arial.ttf", tam)
    except (IOError, OSError):
        try:
            return ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", tam)
        except (IOError, OSError):
            return ImageFont.load_default()

def dibujar_burbuja(draw, x, y, texto, ancho_max, es_user=False, font_size=14):
    fnt = fuente(font_size)
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = linea_actual + " " + palabra if linea_actual else palabra
        ancho = fnt.getbbox(prueba)[2]
        if ancho <= ancho_max - 30:
            linea_actual = prueba
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    alto_linea = fnt.getbbox("Ay")[3] + 4
    alto_burbuja = len(lineas) * alto_linea + 20
    ancho_burbuja = min(ancho_max, max(fnt.getbbox(l)[2] for l in lineas) + 30) if lineas else 50

    if es_user:
        x_burb = ANCHO - ancho_burbuja - 40
        color_fondo = BURBUJA_USER
        color_texto = BLANCO
    else:
        x_burb = 40
        color_fondo = BURBUJA_BOT
        color_texto = TEXTO_CLARO

    draw.rounded_rectangle(
        (x_burb, y, x_burb + ancho_burbuja, y + alto_burbuja),
        radius=12, fill=color_fondo
    )

    for i, linea in enumerate(lineas):
        draw.text((x_burb + 15, y + 10 + i * alto_linea), linea,
                  fill=color_texto, font=fnt)

    return y + alto_burbuja + 10

def captura_inicio():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.rectangle((0, 0, ANCHO, 50), fill=CARD)
    fnt_titulo = fuente(16)
    draw.text((20, 15), "Antidepresión Sonora", fill=BLANCO, font=fnt_titulo)

    # Indicador escribiendo
    fnt_peq = fuente(12)
    draw.text((ANCHO - 100, 18), "Nuevo", fill=ACCENT, font=fnt_peq)

    y_actual = 70

    # Mensaje del bot - bienvenida
    y_actual = dibujar_burbuja(draw, 40, y_actual,
        "Hola, soy tu asistente de bienestar. Estoy aquí para ayudarte a encontrar la música que tu cuerpo y mente necesitan en este momento.",
        400, False, 14)
    y_actual = dibujar_burbuja(draw, 40, y_actual,
        "¿Cuál es el síntoma predominante hoy?", 400, False, 14)

    # Opciones (botones)
    opciones = [
        "Síntomas físicos (tensión, insomnio, dolor)",
        "Síntomas mentales (bloqueo, falta de concentración)",
        "Síntomas emocionales (irritabilidad, tristeza)"
    ]
    y_btn = y_actual + 5
    for op in opciones:
        ancho_op = fnt_peq.getbbox(op)[2] + 30
        draw.rounded_rectangle(
            (40, y_btn, 40 + ancho_op, y_btn + 32),
            radius=16, fill=PRIMARY
        )
        draw.text((55, y_btn + 8), op, fill=TEXTO_CLARO, font=fnt_peq)
        y_btn += 38

    # Input area
    y_input = ALTO - 55
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle((15, y_input + 10, ANCHO - 15, y_input + 45),
                           radius=20, fill="#0d1b2a")
    draw.text((30, y_input + 18), "Describe cómo te sientes...", fill="#546e7a", font=fnt_peq)

    # Send button
    draw.circle((ANCHO - 45, y_input + 27), 15, fill=ACCENT)
    draw.text((ANCHO - 50, y_input + 20), ">", fill=BLANCO, font=fuente(16))

    ruta = os.path.join(OUT_DIR, "captura_pantalla_inicio.png")
    img.save(ruta)
    print(f"OK: {ruta}")

def captura_diagnostico():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.rectangle((0, 0, ANCHO, 50), fill=CARD)
    fnt_titulo = fuente(16)
    draw.text((20, 15), "Antidepresión Sonora", fill=BLANCO, font=fnt_titulo)

    y_actual = 70

    conversacion = [
        (False, "Hola, soy tu asistente de bienestar."),
        (False, "¿Cuál es el síntoma predominante hoy?"),
        (True, "Síntomas físicos (tensión, insomnio, dolor)"),
        (False, "Gracias por compartir eso conmigo."),
        (False, "¿Tus síntomas físicos son más de tipo agudo o crónico?"),
        (True, "Agudo: taquicardia, opresión, crisis de pánico"),
        (False, "Bien, vamos avanzando."),
        (False, "¿Qué enfoque prefieres para manejar esta crisis de ansiedad?"),
        (True, "Bajar pulsaciones con frecuencias específicas"),
        (False, "¿Qué frecuencia Solfeggio prefieres?"),
        (True, "528Hz: Reparación y reducción de cortisol"),
    ]

    for es_user, texto in conversacion:
        if y_actual > ALTO - 120:
            break
        y_actual = dibujar_burbuja(draw, 40, y_actual, texto, 400, es_user, 13)

    # Diagnóstico final
    fnt_diag = fuente(14)
    draw.rounded_rectangle(
        (40, y_actual + 5, ANCHO - 40, y_actual + 120),
        radius=12, fill="#1b5e20"
    )
    draw.text((55, y_actual + 12), "DIAGNÓSTICO", fill="#81c784",
              font=fuente(10))
    draw.text((55, y_actual + 28), "Estrés Agudo con Alta", fill=BLANCO,
              font=fnt_diag)
    draw.text((55, y_actual + 46), "Activación Fisiológica", fill=BLANCO,
              font=fnt_diag)
    draw.text((55, y_actual + 68), "Playlist: 528Hz Reparación y Sanación",
              fill=VERDE_SPOTIFY, font=fnt_diag)
    y_actual += 130

    # Botones post-diagnóstico
    botones = ["Abrir en Spotify", "Nuevo diagnóstico"]
    for btn in botones:
        ancho_btn = fnt_peq.getbbox(btn)[2] + 30
        draw.rounded_rectangle(
            (40, y_actual, 40 + ancho_btn, y_actual + 32),
            radius=16, fill=VERDE_SPOTIFY if "Spotify" in btn else ACCENT
        )
        draw.text((55, y_actual + 8), btn, fill=BLANCO, font=fuente(12))
        y_actual += 0
        break

    # Input area
    y_input = ALTO - 55
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle((15, y_input + 10, ANCHO - 15, y_input + 45),
                           radius=20, fill="#0d1b2a")
    draw.text((30, y_input + 18), "Describe cómo te sientes...", fill="#546e7a", font=fnt_peq)
    draw.circle((ANCHO - 45, y_input + 27), 15, fill=ACCENT)
    draw.text((ANCHO - 50, y_input + 20), ">", fill=BLANCO, font=fuente(16))

    ruta = os.path.join(OUT_DIR, "captura_pantalla_diagnostico.png")
    img.save(ruta)
    print(f"OK: {ruta}")

def captura_spotify():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar with green Spotify dot
    draw.rectangle((0, 0, ANCHO, 50), fill=CARD)
    fnt_titulo = fuente(16)
    draw.text((20, 15), "Antidepresión Sonora", fill=BLANCO, font=fnt_titulo)
    draw.circle((ANCHO - 60, 25), 6, fill=VERDE_SPOTIFY)
    draw.text((ANCHO - 48, 18), "Spotify", fill=VERDE_SPOTIFY, font=fuente(12))

    y_actual = 80

    draw.text((40, y_actual), "Diagnóstico completo", fill=TEXTO_CLARO, font=fuente(14))
    y_actual += 30

    # Card de diagnóstico
    draw.rounded_rectangle((30, y_actual, ANCHO - 30, y_actual + 120),
                           radius=15, fill=CARD)
    draw.text((50, y_actual + 15), "Estrés Agudo con Alta", fill=BLANCO,
              font=fuente(16))
    draw.text((50, y_actual + 38), "Activación Fisiológica", fill=BLANCO,
              font=fuente(16))
    draw.text((50, y_actual + 65), "Frecuencia: 528Hz", fill="#81c784",
              font=fuente(13))
    rec = "Se recomienda la frecuencia 528Hz, conocida como\nla 'frecuencia del amor' o de reparación."
    draw.text((50, y_actual + 90), rec, fill=TEXTO_CLARO, font=fuente(10))
    y_actual += 135

    # Card de playlist
    draw.rounded_rectangle((30, y_actual, ANCHO - 30, y_actual + 100),
                           radius=15, fill="#0d2818")
    draw.circle((55, y_actual + 20), 25, fill=VERDE_SPOTIFY)
    draw.text((30, y_actual + 50), "Spotify", fill=VERDE_SPOTIFY, font=fuente(10), anchor="mt")
    draw.text((95, y_actual + 12), "528Hz Reparación y Sanación", fill=BLANCO,
              font=fuente(14))
    draw.text((95, y_actual + 35), "Frecuencia Solfeggio 528Hz para", fill=TEXTO_CLARO,
              font=fuente(10))
    draw.text((95, y_actual + 50), "reparación celular y reducción", fill=TEXTO_CLARO,
              font=fuente(10))
    draw.text((95, y_actual + 65), "de cortisol.", fill=TEXTO_CLARO, font=fuente(10))
    y_actual += 115

    # Botones de acción
    botones = [("Abrir en Spotify", VERDE_SPOTIFY),
               ("Reproducir ahora", PRIMARY),
               ("Nuevo diagnóstico", ACCENT)]
    for texto, color in botones:
        ancho_btn = fnt_peq.getbbox(texto)[2] + 40
        draw.rounded_rectangle(
            (40, y_actual, 40 + ancho_btn, y_actual + 35),
            radius=18, fill=color
        )
        draw.text((60, y_actual + 10), texto, fill=BLANCO, font=fuente(12))
        y_actual += 42

    # Input
    y_input = ALTO - 55
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle((15, y_input + 10, ANCHO - 15, y_input + 45),
                           radius=20, fill="#0d1b2a")
    draw.circle((ANCHO - 45, y_input + 27), 15, fill=ACCENT)
    draw.text((ANCHO - 50, y_input + 20), ">", fill=BLANCO, font=fuente(16))

    ruta = os.path.join(OUT_DIR, "captura_pantalla_spotify.png")
    img.save(ruta)
    print(f"OK: {ruta}")

fnt_peq = fuente(12)

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    captura_inicio()
    captura_diagnostico()
    captura_spotify()
