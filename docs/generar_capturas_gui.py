from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ANCHO = 520
ALTO = 720
FONDO = "#F5F0EB"
CARD = "#FFFFFF"
PRIMARY = "#D4933A"
PRIMARY_HOVER = "#B87D2E"
TEXT_PRIMARY = "#1D1D1F"
TEXT_SEC = "#86868B"
BORDER = "#E5E0D8"
BURBUJA_BOT = "#FFFFFF"
BURBUJA_USER = "#D4933A"
BURBUJA_USER_TEXT = "#FFFFFF"
CHAT_BG = "#FAF8F5"
INPUT_BG = "#FFFFFF"
INPUT_BORDER = "#E5E0D8"
SPOTIFY_GREEN = "#1DB954"
BLANCO = "#FFFFFF"
NEGRO = "#1D1D1F"
PLAYER_BG = "#1A1A1A"
GOLD = "#D4933A"

OUT_DIR = "docs"


def redondear(imagen, radio):
    mascara = Image.new("L", imagen.size, 0)
    draw = ImageDraw.Draw(mascara)
    draw.rounded_rectangle((0, 0, imagen.size[0], imagen.size[1]), radius=radio, fill=255)
    imagen.putalpha(mascara)
    return imagen


def fuente(tam, bold=False):
    try:
        return ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", tam)
    except (IOError, OSError):
        try:
            return ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", tam) if bold else ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", tam)
        except (IOError, OSError):
            return ImageFont.load_default()


def dibujar_burbuja(draw, x, y, texto, ancho_max, es_user=False, font_size=14):
    fnt = fuente(font_size)
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = linea_actual + " " + palabra if linea_actual else palabra
        bbox = fnt.getbbox(prueba)
        if bbox and bbox[2] <= ancho_max - 30:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    alto_linea = (fnt.getbbox("Ay")[3] - fnt.getbbox("Ay")[1] + 4) if fnt.getbbox("Ay") else 20
    alto_burbuja = len(lineas) * alto_linea + 20
    ancho_lineas = [fnt.getbbox(l)[2] for l in lineas] if lineas else [50]
    ancho_burbuja = min(ancho_max, max(ancho_lineas) + 30)

    if es_user:
        x_burb = ANCHO - ancho_burbuja - 16
        color_fondo = BURBUJA_USER
        color_texto = BURBUJA_USER_TEXT
    else:
        x_burb = 16
        color_fondo = BURBUJA_BOT
        color_texto = TEXT_PRIMARY
        draw.rectangle(
            (x_burb, y + 4, x_burb + ancho_burbuja + 4, y + alto_burbuja + 4),
            fill="#E5E0D8",
        )

    draw.rounded_rectangle(
        (x_burb, y, x_burb + ancho_burbuja, y + alto_burbuja),
        radius=14, fill=color_fondo,
    )

    for i, linea in enumerate(lineas):
        draw.text((x_burb + 15, y + 10 + i * alto_linea), linea,
                  fill=color_texto, font=fnt)

    return y + alto_burbuja + 12


def captura_inicio():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar
    barra_h = 72
    draw.rounded_rectangle((14, 14, ANCHO - 14, 14 + barra_h), radius=16, fill=CARD)
    draw.line((14, 14, ANCHO - 14, 14), fill=BORDER, width=1)

    fnt_titulo = fuente(16)
    draw.text((36, 28), "Antidepresión Sonora", fill=PRIMARY, font=fnt_titulo)
    draw.text((36, 52), "Musicoterapia", fill=TEXT_SEC, font=fuente(9))

    # Botones top-right
    btn_nuevo = (ANCHO - 100, 28, ANCHO - 28, 64)
    draw.rounded_rectangle(btn_nuevo, radius=17, fill=None, outline=BORDER, width=1)
    draw.text((ANCHO - 68, 36), "Nuevo", fill=TEXT_PRIMARY, font=fuente(11))

    # Chat area
    chat_x, chat_y = 14, 96
    draw.rounded_rectangle(
        (chat_x, chat_y, ANCHO - 14, ALTO - 70), radius=16, fill=CHAT_BG,
    )

    y_actual = 110

    # Mensajes del bot
    y_actual = dibujar_burbuja(draw, 0, y_actual,
        "Hola, soy tu asistente de bienestar. Estoy aqui para ayudarte a encontrar la musica que tu cuerpo y mente necesitan en este momento.",
        420, False, 13)

    y_actual = dibujar_burbuja(draw, 0, y_actual,
        "Cual de estos sintomas describe mejor lo que estas sintiendo hoy?",
        420, False, 13)

    # Botones de opciones
    opciones = [
        "Sintomas fisicos (tension, insomnio, dolor)",
        "Sintomas mentales (bloqueo, falta de concentracion)",
        "Sintomas emocionales (irritabilidad, tristeza)",
    ]
    fnt_op = fuente(12)
    y_btn = y_actual + 6
    for op in opciones:
        ancho_op = fnt_op.getbbox(op)[2] + 40
        draw.rounded_rectangle(
            (28, y_btn, 28 + ancho_op, y_btn + 40),
            radius=14, fill=CARD,
        )
        draw.text((48, y_btn + 12), op, fill=TEXT_PRIMARY, font=fnt_op)
        y_btn += 48

    # Input area
    y_input = ALTO - 56
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle(
        (16, y_input + 8, ANCHO - 16, y_input + 48),
        radius=24, fill=INPUT_BG, outline=INPUT_BORDER, width=1,
    )
    draw.text((36, y_input + 18), "Describe como te sientes...", fill=TEXT_SEC, font=fuente(13))

    # Send button
    draw.ellipse((ANCHO - 50, y_input + 10, ANCHO - 14, y_input + 46), fill=GOLD)
    fnt_send = fuente(16)
    draw.text((ANCHO - 36, y_input + 20), ">", fill=BLANCO, font=fnt_send)

    ruta = os.path.join(OUT_DIR, "captura_pantalla_inicio.png")
    img.save(ruta)
    print(f"OK: {ruta}")


def captura_diagnostico():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar
    barra_h = 72
    draw.rounded_rectangle((14, 14, ANCHO - 14, 14 + barra_h), radius=16, fill=CARD)
    draw.text((36, 28), "Antidepresion Sonora", fill=PRIMARY, font=fuente(16))
    draw.text((36, 52), "Musicoterapia", fill=TEXT_SEC, font=fuente(9))

    # Chat area
    draw.rounded_rectangle(
        (14, 96, ANCHO - 14, ALTO - 70), radius=16, fill=CHAT_BG,
    )

    y_actual = 110

    conversacion = [
        (False, "Hola, soy tu asistente de bienestar."),
        (False, "Cual es el sintoma predominante hoy?"),
        (True, "Sintomas fisicos (tension, insomnio, dolor)"),
        (False, "Gracias por compartir eso conmigo."),
        (False, "Tus sintomas fisicos son mas de tipo agudo o cronico?"),
        (True, "Agudo: taquicardia, opresion, crisis de panico"),
        (False, "Bien, vamos avanzando."),
        (False, "Que enfoque prefieres para manejar esta crisis de ansiedad?"),
        (True, "Bajar pulsaciones con frecuencias especificas"),
        (False, "Que frecuencia Solfeggio prefieres?"),
        (True, "528Hz: Reparacion y reduccion de cortisol"),
    ]

    for es_user, texto in conversacion:
        if y_actual > ALTO - 220:
            break
        y_actual = dibujar_burbuja(draw, 0, y_actual, texto, 390, es_user, 12)

    # Diagnostico final card
    dy = y_actual + 10
    draw.rounded_rectangle((28, dy, ANCHO - 28, dy + 100), radius=14, fill="#1A5533")
    draw.text((48, dy + 12), "DIAGNOSTICO", fill="#81C784", font=fuente(10))
    draw.text((48, dy + 28), "Estres Agudo con Alta Activacion Fisiologica",
              fill=BLANCO, font=fuente(14))
    draw.text((48, dy + 50), "528Hz Reparacion y Sanacion",
              fill=SPOTIFY_GREEN, font=fuente(13))
    draw.text((48, dy + 72), "Playlist de Spotify recomendada para vos",
              fill="#A5D6A7", font=fuente(11))

    # Input
    y_input = ALTO - 56
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle(
        (16, y_input + 8, ANCHO - 16, y_input + 48),
        radius=24, fill=INPUT_BG, outline=INPUT_BORDER, width=1,
    )
    draw.text((36, y_input + 18), "Describe como te sientes...", fill=TEXT_SEC, font=fuente(13))
    draw.ellipse((ANCHO - 50, y_input + 10, ANCHO - 14, y_input + 46), fill=GOLD)
    draw.text((ANCHO - 36, y_input + 20), ">", fill=BLANCO, font=fuente(16))

    ruta = os.path.join(OUT_DIR, "captura_pantalla_diagnostico.png")
    img.save(ruta)
    print(f"OK: {ruta}")


def captura_spotify():
    img = Image.new("RGB", (ANCHO, ALTO), FONDO)
    draw = ImageDraw.Draw(img)

    # Top bar
    barra_h = 72
    draw.rounded_rectangle((14, 14, ANCHO - 14, 14 + barra_h), radius=16, fill=CARD)
    draw.text((36, 28), "Antidepresion Sonora", fill=PRIMARY, font=fuente(16))
    draw.text((36, 52), "Musicoterapia", fill=TEXT_SEC, font=fuente(9))

    # Chat area
    draw.rounded_rectangle(
        (14, 96, ANCHO - 14, ALTO - 70), radius=16, fill=CHAT_BG,
    )

    y_actual = 120

    # Diagnostico
    draw.text((36, y_actual), "Diagnostico completo", fill=TEXT_PRIMARY, font=fuente(14))
    y_actual += 30

    # Card diagnostico
    draw.rounded_rectangle((28, y_actual, ANCHO - 28, y_actual + 110), radius=15, fill=CARD, outline=BORDER, width=1)
    draw.text((48, y_actual + 16), "Estres Agudo con Alta Activacion Fisiologica",
              fill=TEXT_PRIMARY, font=fuente(15))
    draw.text((48, y_actual + 42), "Frecuencia Solfeggio 528Hz", fill=GOLD, font=fuente(13))
    draw.text((48, y_actual + 68),
              "Reduccion de cortisol, reparacion celular y regulacion del sistema nervioso autonomo.",
              fill=TEXT_SEC, font=fuente(11))
    y_actual += 125

    # Card playlist Spotify
    draw.rounded_rectangle((28, y_actual, ANCHO - 28, y_actual + 105), radius=15,
                           fill=PLAYER_BG)
    draw.ellipse((48, y_actual + 18, 88, y_actual + 58), fill=SPOTIFY_GREEN)
    draw.text((68, y_actual + 32), "S", fill=BLANCO, font=fuente(22))
    draw.text((105, y_actual + 14), "528Hz Reparacion y Sanacion", fill=BLANCO, font=fuente(15))
    draw.text((105, y_actual + 40), "Frecuencia Solfeggio 528Hz", fill="#A0A0A0", font=fuente(11))
    draw.text((105, y_actual + 58), "para reparacion celular y", fill="#A0A0A0", font=fuente(11))
    draw.text((105, y_actual + 76), "reduccion de cortisol", fill="#A0A0A0", font=fuente(11))
    y_actual += 120

    # Botones de accion
    botones = [
        ("             Abrir en Spotify", SPOTIFY_GREEN),
        ("           Reproducir ahora", GOLD),
        ("        Nuevo diagnostico", None),
    ]
    for texto, color in botones:
        if color:
            draw.rounded_rectangle(
                (28, y_actual, ANCHO - 28, y_actual + 42), radius=14, fill=color,
            )
            draw.text((ANCHO // 2 - 80, y_actual + 12), texto.strip(), fill=BLANCO, font=fuente(13))
        else:
            draw.rounded_rectangle(
                (28, y_actual, ANCHO - 28, y_actual + 42), radius=14, fill=None,
                outline=BORDER, width=1,
            )
            draw.text((ANCHO // 2 - 75, y_actual + 12), texto.strip(), fill=TEXT_SEC, font=fuente(13))
        y_actual += 50

    # Input
    y_input = ALTO - 56
    draw.rectangle((0, y_input, ANCHO, ALTO), fill=CARD)
    draw.rounded_rectangle(
        (16, y_input + 8, ANCHO - 16, y_input + 48),
        radius=24, fill=INPUT_BG, outline=INPUT_BORDER, width=1,
    )
    draw.text((36, y_input + 18), "Describe como te sientes...", fill=TEXT_SEC, font=fuente(13))
    draw.ellipse((ANCHO - 50, y_input + 10, ANCHO - 14, y_input + 46), fill=GOLD)
    draw.text((ANCHO - 36, y_input + 20), ">", fill=BLANCO, font=fuente(16))

    ruta = os.path.join(OUT_DIR, "captura_pantalla_spotify.png")
    img.save(ruta)
    print(f"OK: {ruta}")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    captura_inicio()
    captura_diagnostico()
    captura_spotify()
