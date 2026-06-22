from pathlib import Path
import re

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent.parent
SUPPORT_PHONE = "809-555-1234"
MAX_STEPS_BEFORE_ESCALATION = 3

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


estado = {}

QUICK_OPTIONS = [
    "Sin Internet",
    "Internet lento",
    "Red inalámbrica",
    "IP",
    "DNS",
    "DHCP",
    "Gateway",
    "Cambiar clave",
    "Cambiar nombre",
    "Dispositivos conectados",
    "Seguridad",
    "Reiniciar router",
    "Configurar router",
    "Luces del router",
    "Nueva consulta",
]

YES_WORDS = {"si", "sí", "solucionado", "se soluciono", "se solucionó", "funciono", "funcionó", "ya", "resuelto"}
NO_WORDS = {"no", "no funciona", "no funciono", "no funcionó", "no se soluciono", "no se solucionó", "sigue igual", "igual"}

INTENTS = {
    "sin_internet": [
        "sin internet",
        "no tengo internet",
        "internet caido",
        "internet caído",
        "no funciona internet",
        "no hay red",
        "no carga nada",
    ],
    "internet_lento": ["internet lento", "muy lento", "red lenta", "lag", "se cuelga"],
    "wifi": ["wifi", "wi fi", "wi-fi", "red inalámbrica", "red inalambrica", "no aparece wifi"],
    "ip": ["ip", "dirección ip", "direccion ip", "ipv4", "no tengo ip"],
    "dns": ["dns", "no abre páginas", "no abre paginas", "no carga páginas", "no carga paginas"],
    "gateway": ["gateway", "puerta de enlace"],
    "dhcp": ["dhcp", "no me asigna ip"],
    "cambiar_wifi": ["cambiar clave", "cambiar clave wifi", "cambiar contraseña", "cambiar contraseña wifi", "clave wifi", "clave", "contraseña", "cambiar clave wi fi", "cambiar clave wi-fi"],
    "cambiar_nombre": ["cambiar nombre", "cambiar nombre wifi", "ssid", "nombre de red", "cambiar nombre wi fi", "cambiar nombre wi-fi"],
    "dispositivos": ["dispositivos", "dispositivos conectados", "quien esta conectado", "quién está conectado", "equipos conectados", "intrusos"],
    "seguridad": ["seguridad", "seguridad wifi", "proteger red", "proteger wifi", "hackean wifi"],
    "reiniciar_router": ["reiniciar router", "resetear router", "reinicio router"],
    "configurar_router": ["configurar router", "entrar al router", "19216811", "192.168.1.1"],
    "luces_router": ["luces router", "led router", "luces modem", "luces módem"],
}

ISSUE_STEPS = {
    "sin_internet": {
        "title": "problema de conexión sin Internet",
        "steps": [
            "Paso 1: verifica si el problema ocurre en todos los dispositivos. Si ocurre en todos, apaga el router durante 30 segundos y vuelve a encenderlo.",
            "Paso 2: revisa que los cables de energía, fibra, coaxial o red estén firmes y que las luces principales del router estén encendidas.",
            "Paso 3: conecta un equipo por cable de red si es posible. Si por cable funciona, el problema está en la conexión inalámbrica; si tampoco funciona, puede ser falla del proveedor.",
        ],
    },
    "internet_lento": {
        "title": "lentitud de Internet",
        "steps": [
            "Paso 1: reinicia el router y espera de 2 a 5 minutos para que recupere señal estable.",
            "Paso 2: acércate al router y desconecta descargas, videos o equipos que estén consumiendo mucho ancho de banda.",
            "Paso 3: prueba por cable de red o cambia a la banda de 5 GHz si tu router la tiene disponible.",
        ],
    },
    "wifi": {
        "title": "problema con la red inalámbrica",
        "steps": [
            "Paso 1: confirma si la red aparece en tu dispositivo. Si aparece, olvida la red y vuelve a conectarte con la contraseña correcta.",
            "Paso 2: si la red no aparece, reinicia el router y revisa que la señal inalámbrica esté habilitada desde el panel del router.",
            "Paso 3: prueba con otro dispositivo. Si ninguno ve la red, puede haber una falla en la configuración inalámbrica o en el router.",
        ],
    },
    "ip": {
        "title": "problema de dirección IP",
        "steps": [
            "Paso 1: verifica que tu equipo esté configurado para obtener IP automáticamente.",
            "Paso 2: desconecta y vuelve a conectar la red para renovar la dirección IP.",
            "Paso 3: reinicia el router. Si el equipo sigue sin IP, puede haber un problema con DHCP.",
        ],
    },
    "dns": {
        "title": "problema de DNS",
        "steps": [
            "Paso 1: si hay Internet pero no abren páginas, configura DNS públicos como 8.8.8.8 y 8.8.4.4.",
            "Paso 2: cierra y abre de nuevo el navegador, o prueba entrar a otra página.",
            "Paso 3: reinicia el router y el dispositivo para limpiar la resolución de nombres.",
        ],
    },
    "gateway": {
        "title": "problema de puerta de enlace",
        "steps": [
            "Paso 1: revisa que la puerta de enlace sea la IP del router, normalmente 192.168.1.1 o 192.168.0.1.",
            "Paso 2: si no aparece gateway, configura la red para obtener datos automáticamente.",
            "Paso 3: reinicia la conexión de red y luego el router si el gateway sigue vacío.",
        ],
    },
    "dhcp": {
        "title": "problema de DHCP",
        "steps": [
            "Paso 1: confirma que DHCP esté activado en el router para asignar IP automáticamente.",
            "Paso 2: cambia el equipo a obtener IP automática y reconecta la red.",
            "Paso 3: reinicia el router. Si no asigna IP a ningún equipo, puede requerir revisión técnica.",
        ],
    },
    "cambiar_wifi": {
        "title": "cambio de contraseña",
        "steps": [
            "Paso 1: entra al panel del router desde 192.168.1.1 o 192.168.0.1.",
            "Paso 2: abre la sección Wireless o WLAN y cambia la contraseña de la red.",
            "Paso 3: guarda los cambios y vuelve a conectar todos los dispositivos con la nueva contraseña.",
        ],
    },
    "cambiar_nombre": {
        "title": "cambio de nombre de red",
        "steps": [
            "Paso 1: entra al panel del router desde 192.168.1.1 o 192.168.0.1.",
            "Paso 2: busca SSID, Wireless Name o Nombre de red y escribe el nuevo nombre.",
            "Paso 3: guarda los cambios y reconecta los dispositivos a la red con el nuevo nombre.",
        ],
    },
    "dispositivos": {
        "title": "revisión de dispositivos conectados",
        "steps": [
            "Paso 1: entra al panel del router y busca Connected Devices, Clients o Dispositivos conectados.",
            "Paso 2: identifica equipos desconocidos y bloquéalos si el router lo permite.",
            "Paso 3: cambia la contraseña para expulsar dispositivos no autorizados.",
        ],
    },
    "seguridad": {
        "title": "seguridad de la red",
        "steps": [
            "Paso 1: usa cifrado WPA2 o WPA3. Evita redes abiertas o seguridad WEP.",
            "Paso 2: configura una contraseña larga con letras, números y símbolos.",
            "Paso 3: desactiva WPS si no lo necesitas y cambia la clave si sospechas accesos no autorizados.",
        ],
    },
    "reiniciar_router": {
        "title": "reinicio del router",
        "steps": [
            "Paso 1: apaga el router o desconéctalo de la energía durante 30 segundos.",
            "Paso 2: enciéndelo y espera de 2 a 5 minutos hasta que las luces estén estables.",
            "Paso 3: prueba la conexión desde un dispositivo cercano al router.",
        ],
    },
    "configurar_router": {
        "title": "acceso al panel del router",
        "steps": [
            "Paso 1: abre el navegador y entra a 192.168.1.1 o 192.168.0.1.",
            "Paso 2: inicia sesión con las credenciales del router o las indicadas por tu proveedor.",
            "Paso 3: si no abre, revisa la puerta de enlace del equipo para conocer la dirección real del router.",
        ],
    },
    "luces_router": {
        "title": "luces del router",
        "steps": [
            "Paso 1: revisa si las luces de energía, Internet y señal inalámbrica están encendidas o parpadeando normalmente.",
            "Paso 2: si hay luz roja o apagada en Internet, reinicia el router y revisa cables.",
            "Paso 3: si la luz roja continúa, puede ser una falla de señal o del proveedor.",
        ],
    },
}


def normalizar(texto):
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\sáéíóúüñ]", "", texto)
    return re.sub(r"\s+", " ", texto)


def detectar_intent(message):
    message = normalizar(message)

    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            normalized_keyword = normalizar(keyword)
            if re.search(r"\b" + re.escape(normalized_keyword) + r"\b", message):
                return intent
    return None


def obtener_usuario(user_data):
    if not isinstance(user_data, dict):
        return "anonimo"

    user_code = str(user_data.get("user_code") or "").strip()
    email = str(user_data.get("email") or "").strip()
    full_name = str(user_data.get("full_name") or "").strip()

    return user_code or email or full_name or "anonimo"


def reset_estado(usuario):
    estado[usuario] = {"state": "inicio", "topic": None, "step": 0, "misses": 0}


def get_estado(usuario):
    if usuario not in estado or not isinstance(estado[usuario], dict):
        reset_estado(usuario)
    return estado[usuario]


def opciones_de_revision():
    return ["Se solucionó", "No se solucionó", "Nueva consulta"]


def respuesta_escalamiento(topic=None):
    tema = ISSUE_STEPS.get(topic, {}).get("title", "esta solicitud")
    return (
        f"Lo sentimos, no podemos ayudarte a resolver {tema} desde el asistente virtual. "
        f"Para continuar, comunícate con un personal de soporte al {SUPPORT_PHONE}. "
        "Ten a mano tu nombre, código o ID y una breve descripción del problema."
    )


def respuesta_paso(topic, step_index):
    flow = ISSUE_STEPS[topic]
    total = len(flow["steps"])
    step_number = step_index + 1
    return (
        f"Caso: {flow['title']}.\n"
        f"Revisión {step_number} de {total}: {flow['steps'][step_index]}\n"
        "Cuando termines, dime si se solucionó o no se solucionó."
    )


def iniciar_flujo(usuario, topic):
    session = get_estado(usuario)
    session.update({"state": "revisando", "topic": topic, "step": 0, "misses": 0})
    return respuesta_paso(topic, 0)


def mensaje_es_confirmacion_positiva(message):
    message = normalizar(message)
    return any(word in message for word in YES_WORDS) and "no" not in message


def mensaje_es_confirmacion_negativa(message):
    message = normalizar(message)
    return any(word in message for word in NO_WORDS)


def manejar_revision(usuario, message):
    session = get_estado(usuario)
    topic = session.get("topic")

    if mensaje_es_confirmacion_positiva(message):
        reset_estado(usuario)
        return "Excelente. Me alegra que se haya solucionado. Puedes iniciar otra consulta cuando lo necesites."

    if mensaje_es_confirmacion_negativa(message):
        next_step = int(session.get("step", 0)) + 1
        if not topic or next_step >= min(len(ISSUE_STEPS[topic]["steps"]), MAX_STEPS_BEFORE_ESCALATION):
            reset_estado(usuario)
            return respuesta_escalamiento(topic)

        session["step"] = next_step
        return respuesta_paso(topic, next_step)

    session["misses"] = int(session.get("misses", 0)) + 1
    if session["misses"] >= 2:
        reset_estado(usuario)
        return respuesta_escalamiento(topic)

    return "Para continuar con la revisión, responde con una de estas opciones: Se solucionó o No se solucionó."


def chatbot_logic(usuario, message):
    message = normalizar(message)
    session = get_estado(usuario)

    if session.get("state") == "revisando":
        return manejar_revision(usuario, message)

    intent = detectar_intent(message)

    if intent in ISSUE_STEPS:
        return iniciar_flujo(usuario, intent)

    session["misses"] = int(session.get("misses", 0)) + 1
    if session["misses"] >= 2:
        reset_estado(usuario)
        return respuesta_escalamiento()

    return "No entendí bien tu problema. Elige una opción rápida o descríbelo con palabras como: sin Internet, red inalámbrica, DNS, DHCP, IP o router."


def opciones_para_usuario(usuario):
    session = get_estado(usuario)
    if session.get("state") == "revisando":
        return opciones_de_revision()
    return QUICK_OPTIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()
    usuario = obtener_usuario(data.get("user_data"))

    if not message:
        return jsonify({"response": "Escribe una consulta para poder ayudarte.", "options": QUICK_OPTIONS})

    if normalizar(message) == "nueva consulta":
        reset_estado(usuario)
        return jsonify(
            {
                "response": "Nueva consulta iniciada. Elige el área del problema para comenzar.",
                "options": QUICK_OPTIONS,
            }
        )

    response = chatbot_logic(usuario, message)

    return jsonify({"response": response, "options": opciones_para_usuario(usuario)})


if __name__ == "__main__":
    app.run(debug=True)

