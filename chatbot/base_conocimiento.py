class BaseConocimiento:
    _instancia = None
    _datos = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        self._datos = _CONSTRUIR_BASE()

    def obtener_nodo(self, nodo_id: str) -> dict:
        return self._datos[nodo_id]

    def obtener_todos(self) -> dict:
        return self._datos

    def __len__(self) -> int:
        return len(self._datos)


def _CONSTRUIR_BASE() -> dict[str, dict]:

    base = {}

    base["N01"] = {
        "mensajes": {
            "introduccion": [
                "Hola, soy tu asistente de bienestar. Estoy aquí para ayudarte a encontrar la música que tu cuerpo y mente necesitan en este momento.",
                "Bienvenido. Este es un espacio seguro para ti. Vamos a explorar juntos cómo te sientes.",
                "Qué gusto tenerte aquí. Hoy vamos a trabajar juntos para encontrar la mejor manera de ayudarte.",
                "Hola. Respira profundo. Hoy vamos a enfocarnos en ti y en lo que necesitas.",
                "Me alegra que estés aquí. Vamos a conversar un poco para entender cómo te sientes.",
                "Gracias por confiar en este proceso. Juntos vamos a encontrar lo que necesitas.",
            ],
            "confirmacion": [
                "Gracias por compartir eso conmigo.",
                "Eso me ayuda mucho a entender tu situación.",
                "Te agradezco tu sinceridad, es el primer paso.",
                "Gracias por tu confianza. Cada respuesta me permite ayudarte mejor.",
                "Muy bien, eso es importante. Gracias por decírmelo.",
            ],
            "transicion": [
                "Bien, vamos avanzando. Solo unas preguntas más.",
                "Perfecto, ya tengo una mejor idea. Continuemos.",
                "Gracias. Ahora vamos a profundizar un poco más.",
                "Excelente. Sigamos explorando para encontrar lo ideal para ti.",
                "Muy bien. Vamos al siguiente paso.",
            ],
            "pregunta": [
                "¿Cuál de estos síntomas describe mejor lo que estás sintiendo hoy?",
                "Dime, ¿cuál de estas opciones resuena más con cómo te sientes ahora?",
                "¿Qué tipo de síntomas son los más presentes en tu día a día?",
                "De las siguientes opciones, ¿cuál refleja mejor tu estado actual?",
                "¿Con cuál de estas sensaciones te identificas más hoy?",
            ],
            "explicacion": [
                "Con esta información podré recomendarte la música más adecuada.",
                "Cada respuesta me ayuda a ajustar mejor la recomendación.",
                "Así puedo entender mejor tu estado y encontrar la mejor terapia musical.",
                "Tu perfil se va construyendo con cada respuesta.",
            ],
        },
        "preguntas": [
            "¿Cuál es el síntoma predominante hoy?",
            "¿Qué tipo de malestar estás experimentando principalmente?",
        ],
        "opciones": [
            {"texto": "Síntomas físicos (tensión, insomnio, dolor)", "destino": "N02"},
            {"texto": "Síntomas mentales (bloqueo, falta de concentración)", "destino": "N03"},
            {"texto": "Síntomas emocionales (irritabilidad, tristeza)", "destino": "N04"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N02"] = {
        "mensajes": {
            "introduccion": [
                "Los síntomas físicos son señales importantes que tu cuerpo te envía. Vamos a entenderlos mejor.",
                "El cuerpo siempre habla. Vamos a escuchar lo que te está diciendo.",
                "Los síntomas físicos pueden manifestarse de muchas formas. Cuéntame más.",
                "La tensión en el cuerpo es una respuesta natural al estrés. Vamos a identificar la tuya.",
            ],
            "confirmacion": [
                "Gracias por identificar eso. Es un paso importante.",
                "Entiendo, tu cuerpo está pidiendo atención.",
                "Eso es muy útil para entender tu caso.",
            ],
            "transicion": [
                "Bien, ahora necesito saber un poco más sobre cómo se manifiesta.",
                "Gracias. Vamos a precisar un poco más.",
                "Perfecto. Ahora dime, ¿cómo describirías la intensidad?",
            ],
            "pregunta": [
                "¿Cómo describirías lo que sientes físicamente?",
                "¿Cuál de estas opciones describe mejor tu malestar físico?",
                "¿Tu malestar físico es más agudo o más constante?",
                "Dime, ¿cómo se siente tu cuerpo hoy?",
            ],
            "explicacion": [
                "Distinguir entre agudo y crónico me ayuda a elegir el enfoque correcto.",
                "Cada tipo de tensión tiene una respuesta musical diferente.",
            ],
        },
        "preguntas": [
            "¿Tus síntomas físicos son más de tipo agudo o crónico?",
        ],
        "opciones": [
            {"texto": "Agudo: taquicardia, opresión, crisis de pánico", "destino": "N05"},
            {"texto": "Crónico: cansancio constante, cuerpo pesado, insomnio", "destino": "N06"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N03"] = {
        "mensajes": {
            "introduccion": [
                "La mente puede saturarse cuando hay demasiada información. Vamos a ver qué está pasando.",
                "El estrés mental es muy común hoy en día. Vamos a entender el tuyo.",
                "Los síntomas cognitivos afectan nuestra claridad. Cuéntame qué sientes.",
                "La mente también necesita cuidado. Vamos a ver cómo está la tuya.",
            ],
            "confirmacion": [
                "Gracias por compartirlo. La claridad mental es importante.",
                "Entiendo, la mente puede sentirse abrumada.",
                "Eso es muy valioso para tu diagnóstico.",
            ],
            "transicion": [
                "Bien, ahora vamos a definir mejor el tipo de bloqueo.",
                "Perfecto. Sigamos afinando.",
                "Gracias. Una pregunta más para precisar.",
            ],
            "pregunta": [
                "¿Tu mente se siente bloqueada o más bien acelerada?",
                "¿Cómo describirías tu estado mental hoy?",
                "¿Sientes que no puedes concentrarte o que no puedes dejar de pensar?",
                "Dime, ¿tu mente está en blanco o a mil por hora?",
            ],
            "explicacion": [
                "Saber si es bloqueo o hiperactividad cambia completamente el enfoque.",
                "Cada estado mental necesita un tipo diferente de estímulo musical.",
            ],
        },
        "preguntas": [
            "¿Tu síntoma cognitivo principal es bloqueo o hiperactividad mental?",
        ],
        "opciones": [
            {"texto": "Bloqueo: no puedo concentrarme, mente en blanco", "destino": "N07"},
            {"texto": "Hiperactividad: overthinking, mente acelerada", "destino": "N08"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N04"] = {
        "mensajes": {
            "introduccion": [
                "Las emociones son una brújula importante. Vamos a ver qué está sintiendo tu corazón.",
                "Lo emocional es igual de importante que lo físico. Cuéntame cómo te sientes.",
                "Las emociones nos dan pistas valiosas. Vamos a explorarlas.",
                "La irritabilidad, la tristeza o la apatía son señales. Vamos a entenderlas.",
            ],
            "confirmacion": [
                "Gracias por conectar con tus emociones. Es valiente.",
                "Reconocer lo que sientes es el primer paso para sanar.",
                "Eso es importante. Tus emociones importan.",
            ],
            "transicion": [
                "Bien, vamos a profundizar en esa emoción.",
                "Gracias. Ahora necesito saber un poco más.",
                "Perfecto. Sigamos ese hilo emocional.",
            ],
            "pregunta": [
                "¿Tu estado emocional se acerca más a la frustración o a la tristeza?",
                "¿Qué predomina hoy: el enojo o la apatía?",
                "Dime, ¿sientes más irritación o más desánimo?",
                "¿Cómo describirías tu estado de ánimo predominante?",
            ],
            "explicacion": [
                "La frustración y la tristeza se tratan de forma muy distinta musicalmente.",
                "Identificar la emoción exacta me permite afinar la terapia.",
            ],
        },
        "preguntas": [
            "¿Tu estado emocional es más de frustración/enojo o de tristeza/apatía?",
        ],
        "opciones": [
            {"texto": "Frustración, enojo, irritabilidad acumulada", "destino": "N09"},
            {"texto": "Tristeza, desánimo, apatía, melancolía", "destino": "N10"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N05"] = {
        "mensajes": {
            "introduccion": [
                "Parece que estás pasando por un momento de mucha activación. Vamos a encontrar cómo bajarla.",
                "La ansiedad aguda es intensa, pero hay formas de canalizarla. Vamos a ver cuál es la mejor para ti.",
                "Cuando el cuerpo está en alerta máxima, la música puede ser un ancla. Veamos qué necesitas.",
                "Entiendo que la taquicardia y la opresión son abrumadoras. Vamos a trabajar en ello.",
            ],
            "confirmacion": [
                "Gracias por identificar ese nivel de intensidad.",
                "Eso me da una idea clara de lo que estás viviendo.",
                "Reconocerlo es parte del proceso de calma.",
            ],
            "transicion": [
                "Bien, ahora vamos a elegir el mejor enfoque para ti.",
                "Perfecto. Solo una elección más y tendremos tu recomendación.",
                "Gracias. Ahora decide cómo prefieres abordar esta calma.",
            ],
            "pregunta": [
                "¿Qué enfoque crees que te ayudaría más ahora?",
                "¿Prefieres algo que baje tus pulsaciones o algo que te distraiga por completo?",
                "Para este momento de crisis, ¿qué crees que necesitas más?",
                "Dime, ¿tu cuerpo pide calma profunda o desconexión total?",
            ],
            "explicacion": [
                "Las frecuencias específicas trabajan directamente sobre el sistema nervioso.",
                "Los sonidos naturales pueden ayudar a desconectar la mente del foco de ansiedad.",
            ],
        },
        "preguntas": [
            "¿Qué enfoque prefieres para manejar esta crisis de ansiedad?",
        ],
        "opciones": [
            {"texto": "Bajar pulsaciones con frecuencias específicas", "destino": "N11"},
            {"texto": "Distracción total con sonidos de la naturaleza", "destino": "N12"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Estrés Agudo con Componente de Ansiedad Elevada",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N06"] = {
        "mensajes": {
            "introduccion": [
                "El agotamiento crónico es una señal de que necesitas descanso profundo. Vamos a encontrar la música adecuada.",
                "Parece que llevas mucho tiempo funcionando en reserva. Tu cuerpo necesita recuperación.",
                "El burnout no se resuelve con una siesta corta. Necesitas un ambiente sonoro que te permita realmente descansar.",
                "La fatiga constante puede aliviarse con la música adecuada. Vamos a encontrarla.",
            ],
            "confirmacion": [
                "Gracias por reconocer el agotamiento. Es el primer paso para recuperarte.",
                "Entiendo, el cansancio acumulado pesa mucho.",
                "Eso es importante. Tu cuerpo te está pidiendo una pausa.",
            ],
            "transicion": [
                "Bien, vamos a elegir el sonido que te ayude a descansar.",
                "Perfecto. Una decisión más y tendremos tu recomendación.",
                "Gracias. Ahora elige el tipo de descanso que necesitas.",
            ],
            "pregunta": [
                "¿Qué tipo de descanso necesitas más en este momento?",
                "¿Prefieres algo que te ayude a conciliar el sueño o un ambiente sonoro más denso?",
                "Para tu nivel de agotamiento, ¿qué crees que necesitas?",
            ],
            "explicacion": [
                "La música ambiental densa ayuda a desconectar del mundo exterior.",
                "La música para dormir profundo trabaja en frecuencias muy bajas.",
            ],
        },
        "preguntas": [
            "¿Qué necesitas más: conciliar el sueño o un ambiente de relajación profunda?",
        ],
        "opciones": [
            {"texto": "Conciliar el sueño con sonidos ambientales densos", "destino": "N13"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Fatiga Crónica por Estrés Acumulado (Burnout)",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N07"] = {
        "mensajes": {
            "introduccion": [
                "El bloqueo mental puede ser frustrante. Vamos a encontrar la llave musical que te ayude a desbloquearte.",
                "Sentir que la mente no responde es común cuando hay sobrecarga. Vamos a reactivarla.",
                "El bloqueo creativo no significa que no tengas ideas, solo que necesitas un reenfoque.",
                "Vamos a usar la música para re-sincronizar tu mente y encontrar claridad.",
            ],
            "confirmacion": [
                "Gracias por reconocer el bloqueo. Es el primer paso para superarlo.",
                "Entiendo, esa sensación de mente en blanco es agotadora.",
                "Reconocerlo ya es un avance importante.",
            ],
            "transicion": [
                "Perfecto. Vamos a elegir el sonido que te ayude a recuperar el foco.",
                "Bien, solo un paso más y tendremos la recomendación ideal.",
                "Gracias. Ahora elige cómo quieres enfocar tu mente.",
            ],
            "pregunta": [
                "¿Qué tipo de estímulo crees que necesita tu mente para desbloquearse?",
                "¿Prefieres algo que sincronice tus ondas cerebrales o un ritmo suave constante?",
                "Para el bloqueo mental, ¿qué enfoque te llama más la atención?",
            ],
            "explicacion": [
                "Los beats binaurales ayudan a sincronizar los hemisferios cerebrales.",
                "Los ritmos suaves y constantes ayudan a establecer un flujo de trabajo.",
            ],
        },
        "preguntas": [
            "¿Cómo prefieres abordar tu bloqueo mental?",
        ],
        "opciones": [
            {"texto": "Foco profundo con pulsos binaurales", "destino": "N14"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Bloqueo Mental por Sobrecarga Cognitiva",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N08"] = {
        "mensajes": {
            "introduccion": [
                "Tener la mente a mil por hora puede ser agotador. Vamos a encontrar un ritmo que la serene.",
                "El overthinking es como una rueda que no para. La música adecuada puede ponerle freno.",
                "Los pensamientos acelerados necesitan un ancla rítmica. Vamos a encontrarla.",
                "Tu mente está trabajando en exceso. Vamos a darle un acompañamiento sonoro que la calme.",
            ],
            "confirmacion": [
                "Gracias por identificar esa hiperactividad mental.",
                "Entiendo, la mente que no para puede ser muy desgastante.",
                "Reconocerlo es importante para encontrar la solución adecuada.",
            ],
            "transicion": [
                "Perfecto. Vamos a elegir el ritmo que mejor se adapte a tu mente.",
                "Bien, solo una decisión más y tendremos tu recomendación.",
                "Gracias. Ahora elige cómo quieres calmarla.",
            ],
            "pregunta": [
                "¿Qué tipo de acompañamiento musical crees que necesita tu mente?",
                "Para una mente acelerada, ¿qué prefieres?",
                "¿Qué ritmo crees que podría ayudar a bajar la velocidad de tus pensamientos?",
            ],
            "explicacion": [
                "El Lo-Fi tiene un BPM constante que ayuda a regular el ritmo mental.",
                "Los ritmos suaves permiten que la mente se aquiete gradualmente.",
            ],
        },
        "preguntas": [
            "¿Qué enfoque prefieres para calmar tu mente acelerada?",
        ],
        "opciones": [
            {"texto": "Flujo constante con ritmos Lo-Fi suaves", "destino": "N15"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Ansiedad Cognitiva con Hiperactividad Mental (Overthinking)",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N09"] = {
        "mensajes": {
            "introduccion": [
                "La frustración y el enojo son energía acumulada que necesita un canal de salida. La música puede ser ese canal.",
                "La ira no es mala, solo necesita expresarse de forma constructiva. Vamos a encontrar cómo.",
                "Cuando la frustración se acumula, el cuerpo pide liberación. La música instrumental puede ayudarte.",
                "El enojo contenido puede transformarse a través del sonido. Vamos a explorar cómo.",
            ],
            "confirmacion": [
                "Gracias por reconocer esa frustración. Es válido sentirla.",
                "Entiendo, a veces la ira es necesaria y hay que canalizarla.",
                "Reconocer el enojo es parte del proceso de liberación.",
            ],
            "transicion": [
                "Perfecto. Vamos a elegir la música que te ayude a liberar esa energía.",
                "Bien, solo un paso más y tendremos tu recomendación.",
                "Gracias. Ahora elige cómo quieres canalizar esa energía.",
            ],
            "pregunta": [
                "¿Qué tipo de liberación musical crees que necesitas?",
                "Para canalizar la frustración, ¿qué prefieres?",
                "¿Cómo te gustaría expresar esa energía a través de la música?",
            ],
            "explicacion": [
                "El Post-Rock tiene una progresión que acompaña la catarsis emocional.",
                "Las composiciones instrumentales con clímax permiten liberar tensión acumulada.",
            ],
        },
        "preguntas": [
            "¿Cómo prefieres canalizar tu frustración o enojo?",
        ],
        "opciones": [
            {"texto": "Descarga rítmica con Post-Rock instrumental", "destino": "N16"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Frustración Acumulada con Necesidad de Catarsis",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N10"] = {
        "mensajes": {
            "introduccion": [
                "La tristeza y la apatía también necesitan ser escuchadas. Vamos a encontrar la música que te acompañe en este momento.",
                "No todas las emociones necesitan ser arregladas, a veces solo necesitan ser validadas. La música puede hacer eso.",
                "El desánimo es una emoción válida. Vamos a encontrar un sonido que te haga compañía.",
                "A veces lo que necesitamos es sentir que no estamos solos. La música puede ser esa compañía.",
            ],
            "confirmacion": [
                "Gracias por compartir tu tristeza. Es un acto de valentía.",
                "Entiendo, la apatía puede ser muy pesada de llevar.",
                "Reconocerla es el primer paso para sentirte mejor.",
            ],
            "transicion": [
                "Bien. Vamos a encontrar la música que mejor te acompañe en este momento.",
                "Perfecto. Solo una elección más y tendremos tu recomendación.",
                "Gracias. Ahora elige cómo quieres sentirte acompañado.",
            ],
            "pregunta": [
                "¿Qué tipo de compañía musical crees que necesitas ahora?",
                "Para este momento de melancolía, ¿qué prefieres?",
                "¿Qué ambiente sonoro te gustaría que te envolviera?",
            ],
            "explicacion": [
                "A veces necesitamos sonidos densos que nos envuelvan, otras veces ritmos suaves que nos sostengan.",
                "Cada tipo de melancolía encuentra consuelo en un tipo diferente de música.",
            ],
        },
        "preguntas": [
            "¿Qué tipo de ambiente musical te gustaría para acompañar tu estado de ánimo?",
        ],
        "opciones": [
            {"texto": "Sonidos ambientales densos que me envuelvan", "destino": "N13"},
            {"texto": "Ritmos suaves y cálidos que me sostengan", "destino": "N15"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "Baja Energía Emocional con Tendencia a la Melancolía",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N11"] = {
        "mensajes": {
            "introduccion": [
                "Las frecuencias específicas tienen un efecto directo sobre nuestro sistema nervioso. Vamos a elegir la adecuada.",
                "Las frecuencias Solfeggio son conocidas por sus propiedades reparadoras. Elige la que más resuene contigo.",
                "Cada frecuencia tiene una propiedad diferente. Vamos a encontrar la que tu cuerpo necesita.",
            ],
            "confirmacion": [
                "Buena elección. Las frecuencias son muy poderosas.",
                "Excelente. Cada frecuencia trabaja de forma diferente.",
            ],
            "transicion": [
                "Perfecto. Estamos muy cerca de tu recomendación final.",
                "Bien, solo un paso más y tendrás tu playlist personalizada.",
            ],
            "pregunta": [
                "¿Qué tipo de frecuencia crees que necesita tu cuerpo ahora?",
                "¿Prefieres una frecuencia reparadora o una de calma profunda?",
                "¿Tu cuerpo pide reparación o calma?",
            ],
            "explicacion": [
                "La frecuencia 528Hz está asociada con la reparación celular y reducción de cortisol.",
                "La frecuencia 432Hz se relaciona con la armonización y la calma profunda.",
            ],
        },
        "preguntas": [
            "¿Qué frecuencia Solfeggio prefieres?",
        ],
        "opciones": [
            {"texto": "528Hz: Reparación y reducción de cortisol", "destino": "N17"},
            {"texto": "432Hz: Calma profunda y armonización", "destino": "N18"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N12"] = {
        "mensajes": {
            "introduccion": [
                "Los sonidos de la naturaleza son uno de los anclajes más poderosos para la mente ansiosa. Vamos a elegir tu paisaje sonoro.",
                "La naturaleza tiene su propia música. Vamos a encontrar la que mejor te ayude a desconectar.",
                "Los paisajes sonoros pueden transportar tu mente a un lugar seguro. Elige tu refugio.",
            ],
            "confirmacion": [
                "Excelente elección. La naturaleza nunca falla.",
                "Los sonidos naturales son muy efectivos para la ansiedad.",
            ],
            "transicion": [
                "Perfecto. Ya casi tenemos tu recomendación completa.",
                "Bien, solo una decisión más y tendrás tu playlist.",
            ],
            "pregunta": [
                "¿Qué paisaje sonoro natural te llama más la atención?",
                "¿Prefieres la lluvia o prefieres un sonido más constante y profundo?",
                "¿Qué sonido de la naturaleza te gustaría que te envolviera?",
            ],
            "explicacion": [
                "La lluvia actúa como un escudo acústico que aísla la mente.",
                "El ruido marrón y blanco tienen propiedades específicas para apagar el ruido mental.",
            ],
        },
        "preguntas": [
            "¿Qué sonido de la naturaleza prefieres?",
        ],
        "opciones": [
            {"texto": "Lluvia y tormenta: escudo acústico", "destino": "N19"},
            {"texto": "Ruido marrón profundo: apagar ruido mental", "destino": "N20"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N13"] = {
        "mensajes": {
            "introduccion": [
                "La música ambiental densa te permite desconectarte del mundo exterior y entrar en tu propio espacio.",
                "Los sonidos de texturas densas y lentas son ideales para cuando necesitas aislamiento sensorial.",
                "El Drone y Dark Ambient crean un manto sonoro que te protege del exterior.",
            ],
            "confirmacion": [
                "Buena elección. La densidad sonora es muy envolvente.",
                "Excelente. El sonido ambiental denso es muy reparador.",
            ],
            "transicion": [
                "Perfecto. Estamos a un paso de tu recomendación final.",
                "Bien, elige el tipo de ambiente denso que prefieres.",
            ],
            "pregunta": [
                "¿Qué tipo de ambiente denso prefieres?",
                "¿Buscas algo oscuro y profundo o algo más etéreo y espacial?",
                "¿Cómo te gustaría que fuera el manto sonoro que te envuelva?",
            ],
            "explicacion": [
                "El Dark Ambient crea una atmósfera de introspección profunda.",
                "La música espacial para dormir induce estados de relajación muy profundos.",
            ],
        },
        "preguntas": [
            "¿Qué tipo de ambiente sonoro denso prefieres?",
        ],
        "opciones": [
            {"texto": "Dark Ambient / Drone: introspección profunda", "destino": "N21"},
            {"texto": "Deep Sleep: música espacial para descanso", "destino": "N22"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N14"] = {
        "mensajes": {
            "introduccion": [
                "Los beats binaurales utilizan frecuencias específicas para sincronizar tus ondas cerebrales. Es como un entrenamiento para tu mente.",
                "La neuro-acústica puede ayudarte a alcanzar estados de concentración profunda. Vamos a ello.",
                "Los pulsos auditivos binaurales son una herramienta poderosa para el enfoque mental.",
            ],
            "confirmacion": [
                "Excelente elección. Los binaurales son muy efectivos.",
                "Los beats binaurales tienen respaldo científico para el enfoque.",
            ],
            "transicion": [
                "Perfecto. Ya casi tenemos tu recomendación.",
                "Bien, un último paso y tendrás tu playlist.",
            ],
            "pregunta": [
                "¿Estás listo para trabajar con ondas alpha?",
                "¿Quieres activar el enfoque profundo con beats binaurales?",
            ],
            "explicacion": [
                "Las ondas Alpha (8-12Hz) están asociadas con la concentración relajada y el aprendizaje.",
            ],
        },
        "preguntas": [
            "¿Quieres activar tu enfoque con beats binaurales?",
        ],
        "opciones": [
            {"texto": "Sí, quiero activar ondas alpha para enfocarme", "destino": "N23"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N15"] = {
        "mensajes": {
            "introduccion": [
                "El Lo-Fi Chillhop es como un abrazo sonoro para una mente acelerada. Sus beats suaves y constantes ayudan a regular el ritmo mental.",
                "La música Lo-Fi tiene un BPM ideal para calmar la mente sin dormirla. Es el punto medio perfecto.",
                "Los ritmos suaves del Chillhop crean un ambiente acogedor para tu mente.",
            ],
            "confirmacion": [
                "Buena elección. El Lo-Fi es perfecto para mentes activas.",
                "El Chillhop es ideal para encontrar ese punto de calma activa.",
            ],
            "transicion": [
                "Perfecto. Ya casi tenemos tu recomendación personalizada.",
                "Bien, solo un paso más y tendrás tu playlist.",
            ],
            "pregunta": [
                "¿Estás listo para sumergirte en el Lo-Fi?",
                "¿Quieres dejarte llevar por los beats suaves del Chillhop?",
            ],
            "explicacion": [
                "El Lo-Fi sin letra permite que la mente se calme sin distracciones lingüísticas.",
            ],
        },
        "preguntas": [
            "¿Quieres sumergirte en el Lo-Fi Chillhop?",
        ],
        "opciones": [
            {"texto": "Sí, quiero beats Lo-Fi suaves y constantes", "destino": "N24"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    base["N16"] = {
        "mensajes": {
            "introduccion": [
                "El Post-Rock instrumental es un viaje sonoro que te permite soltar la frustración a través de sus crescendos emocionales.",
                "La música instrumental con evolución y clímax es ideal para canalizar la energía acumulada.",
                "El Post-Rock te lleva de la calma a la explosión emocional y viceversa. Perfecto para la catarsis.",
            ],
            "confirmacion": [
                "Excelente elección. El Post-Rock es catártico.",
                "El Post-Rock instrumental es ideal para liberar emociones contenidas.",
            ],
            "transicion": [
                "Perfecto. Estamos listos para tu recomendación final.",
                "Bien, ya tenemos todo para tu playlist personalizada.",
            ],
            "pregunta": [
                "¿Estás listo para un viaje sonoro de catarsis?",
                "¿Quieres dejar que el Post-Rock te lleve?",
            ],
            "explicacion": [
                "El Post-Rock instrumental tiene una progresión que acompaña perfectamente la liberación emocional.",
            ],
        },
        "preguntas": [
            "¿Estás listo para liberar tu frustración con Post-Rock?",
        ],
        "opciones": [
            {"texto": "Sí, quiero un viaje catártico de Post-Rock", "destino": "N25"},
        ],
        "spotify_query": "",
        "spotify_market": "",
        "spotify_playlist_id": "",
        "spotify_playlist_url": "",
        "playlist_nombre": "",
        "playlist_descripcion": "",
        "diagnostico": "",
        "recomendacion": "",
        "esHoja": False,
    }

    def _nodo_hoja(
        spotify_query: str,
        diagnostico: str,
        recomendacion: str,
        nombre: str = "",
        descripcion: str = "",
    ) -> dict:
        return {
            "mensajes": {
                "introduccion": [
                    "He completado tu evaluación. Ahora tengo una recomendación personalizada para ti.",
                    "Ya tengo suficiente información. Déjame preparar tu recomendación.",
                    "Gracias por tu paciencia. He encontrado la música ideal para ti.",
                ],
                "confirmacion": [],
                "transicion": [],
                "pregunta": [],
                "explicacion": [
                    "Basándome en tus respuestas, he seleccionado la playlist más adecuada.",
                    "Tu perfil sonoro está listo. La música que te recomiendo tiene propiedades terapéuticas específicas.",
                ],
            },
            "preguntas": [],
            "opciones": [],
            "spotify_query": spotify_query,
            "spotify_market": "",
            "spotify_playlist_id": "",
            "spotify_playlist_url": "",
            "playlist_nombre": nombre,
            "playlist_descripcion": descripcion,
            "diagnostico": diagnostico,
            "recomendacion": recomendacion,
            "esHoja": True,
        }

    base["N17"] = _nodo_hoja(
        spotify_query="528hz solfeggio healing frequency",
        diagnostico="Estrés Agudo con Alta Activación Fisiológica",
        recomendacion="Se recomienda la frecuencia 528Hz, conocida como la 'frecuencia del amor' o de reparación. "
                       "Esta frecuencia está asociada con la reducción del cortisol y la promoción de la reparación celular. "
                       "Escúchala con audífonos en un lugar tranquilo, preferiblemente al atardecer o antes de dormir. "
                       "Respira profundamente mientras la escuchas y permite que las vibraciones atraviesen tu cuerpo.",
        nombre="528Hz Reparación y Sanación",
        descripcion="Frecuencia Solfeggio 528Hz para reparación celular y reducción de cortisol.",
    )

    base["N18"] = _nodo_hoja(
        spotify_query="432hz calming deep relaxation music",
        diagnostico="Estrés Agudo con Necesidad de Calma Profunda",
        recomendacion="Se recomienda la frecuencia 432Hz, conocida por su efecto armonizante y relajante. "
                       "Esta frecuencia resuena con la vibración natural del universo y promueve una sensación de paz interior. "
                       "Siéntate o recuéstate, cierra los ojos y deja que la música te envuelva. "
                       "Concéntrate en tu respiración mientras las ondas de 432Hz te guían hacia un estado de calma profunda.",
        nombre="432Hz Calma Profunda",
        descripcion="Frecuencia 432Hz para armonización y relajación general.",
    )

    base["N19"] = _nodo_hoja(
        spotify_query="rain thunderstorm sounds for sleep relaxation",
        diagnostico="Crisis de Ansiedad con Necesidad de Escudo Acústico",
        recomendacion="Se recomienda el sonido de lluvia y tormenta como escudo acústico. "
                       "El sonido constante de la lluvia actúa como ruido rosa, que enmascara los sonidos disruptivos "
                       "y crea un ambiente seguro y predecible para tu mente. "
                       "Recuéstate, ponte cómodo y deja que la lluvia lave tus pensamientos ansiosos. "
                       "Imagina que cada gota de lluvia se lleva un pensamiento de estrés.",
        nombre="Lluvia y Tormenta para Dormir",
        descripcion="Sonidos de lluvia y truenos como escudo acústico contra la ansiedad.",
    )

    base["N20"] = _nodo_hoja(
        spotify_query="brown noise deep focus sleep",
        diagnostico="Ansiedad Aguda con Ruido Mental Persistente",
        recomendacion="Se recomienda el Ruido Marrón Profundo, ideal para apagar el ruido mental inmediato. "
                       "A diferencia del ruido blanco, el ruido marrón tiene frecuencias más graves que resultan más "
                       "naturales y menos irritantes para el oído humano. "
                       "Es perfecto para cuando necesitas silenciar los pensamientos intrusivos de forma inmediata. "
                       "Úsalo con audífonos para obtener el máximo efecto de aislamiento sensorial.",
        nombre="Ruido Marrón Profundo",
        descripcion="Ruido marrón profundo para apagar el ruido mental inmediato.",
    )

    base["N21"] = _nodo_hoja(
        spotify_query="dark ambient drone space music",
        diagnostico="Agotamiento Crónico con Necesidad de Desconexión Profunda",
        recomendacion="Se recomienda Dark Ambient / Drone Espacial para inducir estados de despersonalización "
                       "del estrés. Los drones graves y las texturas densas crean un manto sonoro que te separa "
                       "del mundo exterior y te permite flotar en un espacio de no-pensamiento. "
                       "Esta música funciona mejor en oscuridad total, con audífonos y sin interrupciones. "
                       "Permítete no pensar, solo sentir las vibraciones.",
        nombre="Dark Ambient Espacial",
        descripcion="Dark Ambient y Drone para desconexión profunda del estrés.",
    )

    base["N22"] = _nodo_hoja(
        spotify_query="deep sleep space music delta waves",
        diagnostico="Insomnio por Estrés Crónico con Fatiga Profunda",
        recomendacion="Se recomienda Deep Sleep Space Music con ondas delta (0.5 BPM). "
                       "Esta música está diseñada específicamente para inducir el sueño profundo mediante "
                       "pulsos de frecuencia extremadamente baja que sincronizan el cerebro con ondas delta. "
                       "Establece una rutina: pon la música 30 minutos antes de dormir, atenúa las luces, "
                       "y permite que los sonidos espaciales te lleven suavemente hacia el sueño. "
                       "No uses pantallas mientras la escuchas para maximizar su efecto.",
        nombre="Deep Sleep Space Music",
        descripcion="Música espacial para dormir profundamente con ondas delta.",
    )

    base["N23"] = _nodo_hoja(
        spotify_query="binaural beats alpha waves focus concentration",
        diagnostico="Bloqueo Mental por Sobrecarga Cognitiva",
        recomendacion="Se recomiendan Beats Binaurales con Ondas Alpha (8-12Hz) para restaurar el enfoque. "
                       "Los beats binaurales funcionan reproduciendo frecuencias ligeramente diferentes en cada oído, "
                       "lo que obliga al cerebro a sincronizarse y producir ondas alpha, asociadas con la concentración "
                       "relajada y el estado de flujo. "
                       "Usa audífonos estéreo obligatoriamente. Escúchalos mientras trabajas o estudias para "
                       "mantener un estado de concentración sostenida.",
        nombre="Ondas Alpha para Enfoque",
        descripcion="Beats binaurales con ondas Alpha (8-12Hz) para concentración y enfoque.",
    )

    base["N24"] = _nodo_hoja(
        spotify_query="lo fi chillhop beats study relax without lyrics",
        diagnostico="Ansiedad Cognitiva con Hiperactividad Mental",
        recomendacion="Se recomienda Lo-Fi Chillhop sin letra para calmar la mente sobreestimulada. "
                       "El Lo-Fi tiene un BPM constante entre 60 y 80, que es el rango ideal para inducir "
                       "un estado de calma activa. La ausencia de letra evita que tu mente se distraiga "
                       "con procesamiento lingüístico adicional. "
                       "Perfecto para estudiar, trabajar o simplemente relajarte mientras mantienes la mente ocupada "
                       "pero no acelerada. Acompáñalo con una taza de té o café.",
        nombre="Lo-Fi Beats sin Letra",
        descripcion="Chillhop y Lo-Fi suave para mentes sobreestimuladas.",
    )

    base["N25"] = _nodo_hoja(
        spotify_query="post rock instrumental cinematic crescendo",
        diagnostico="Frustración Acumulada con Necesidad de Catarsis Emocional",
        recomendacion="Se recomienda Post-Rock Instrumental Cinemático para canalizar la frustración. "
                       "El Post-Rock se caracteriza por sus crescendos emocionales que construyen tensión "
                       "gradualmente y la liberan en explosiones sonoras catárticas. "
                       "Es ideal para cuando necesitas sacar la frustración de forma segura y constructiva. "
                       "Escúchalo con audífonos a un volumen moderado-alto. Permítete moverte, cerrar los ojos "
                       "y dejar que la música te lleve a través del clímax hasta la resolución.",
        nombre="Post-Rock Instrumental Catártico",
        descripcion="Post-Rock instrumental con crescendos para liberación emocional.",
    )

    return base
