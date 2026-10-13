
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# 1. CONFIGURACIÃ“N DE LA PÃGINA
# ============================================================

st.set_page_config(
    page_title="Astra - Asistente Inteligente",
    page_icon="ðŸ¤–",
    layout="centered"
)

st.title("ðŸ¤– Asistente Virtual Astra")
st.caption(
    "UAdeO | Sistemas Inteligentes | "
    "Dra. Aiblis Susej Herrera Palafox"
)

st.markdown("---")

# ============================================================
# 2. CONFIGURACIÃ“N SEGURA DE LA API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Intentar obtener la clave desde Streamlit Cloud
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = None

if not api_key:
    st.error(
        "No se encontrÃ³ GEMINI_API_KEY. "
        "Configura tu archivo .env o los secretos de Streamlit."
    )
    st.stop()

# ============================================================
# 3. CONFIGURACIÃ“N DEL MODELO GEMINI
# ============================================================

MODELO = "gemini-2.5-flash-lite"

SYSTEM_INSTRUCTION = """
Eres Astra, un asistente acadÃ©mico inteligente desarrollado
para la materia de Sistemas Inteligentes de la UAdeO.

Tus objetivos son:

1. Explicar conceptos de inteligencia artificial.
2. Ayudar con programaciÃ³n en Python.
3. Explicar agentes inteligentes y redes neuronales.
4. Responder preguntas acadÃ©micas claramente.
5. Proporcionar ejemplos prÃ¡cticos.
6. Mantener un tono formal, amable y respetuoso.

Si te preguntan por fechas de entrega o actividades,
indica que deben consultar las instrucciones de la
Dra. Aiblis Susej Herrera Palafox.

Responde siempre en espaÃ±ol, salvo que el usuario
solicite otro idioma.

Utiliza Markdown cuando sea Ãºtil.
"""

CONFIG_PERSONALIZADA = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.7,
    max_output_tokens=1200
)

# ============================================================
# 4. CREAR CLIENTE GEMINI
# ============================================================

@st.cache_resource
def crear_cliente(clave):
    return genai.Client(api_key=clave)

try:
    client = crear_cliente(api_key)
except Exception as e:
    st.error(f"Error al conectar con Gemini: {e}")
    st.stop()

# ============================================================
# 5. INICIALIZAR MEMORIA DE CONVERSACIÃ“N
# ============================================================

MENSAJE_INICIAL = (
    "Â¡Hola! Soy Astra, tu asistente inteligente. "
    "Â¿En quÃ© tema de Sistemas Inteligentes puedo ayudarte?"
)

def crear_chat():
    return client.chats.create(
        model=MODELO,
        config=CONFIG_PERSONALIZADA
    )

if "chat_session" not in st.session_state:
    st.session_state.chat_session = crear_chat()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": MENSAJE_INICIAL
        }
    ]

# ============================================================
# 6. BARRA LATERAL
# ============================================================

with st.sidebar:

    st.header("âš™ï¸ ConfiguraciÃ³n")

    st.success("Gemini configurado")

    st.write("**Asistente:** Astra")
    st.write("**Modelo:** Gemini 2.5 Flash-Lite")
    st.write("**Materia:** Sistemas Inteligentes")

    st.markdown("---")

    st.subheader("Opciones")

    if st.button(
        "ðŸ§¹ Limpiar conversaciÃ³n",
        use_container_width=True
    ):

        st.session_state.chat_session = crear_chat()

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "ConversaciÃ³n reiniciada. Â¿En quÃ© puedo ayudarte?"
            }
        ]

        st.rerun()

    st.markdown("---")

    st.info(
        "Astra utiliza inteligencia artificial "
        "de Google Gemini para responder preguntas."
    )

# ============================================================
# 7. MOSTRAR HISTORIAL DE MENSAJES
# ============================================================

for mensaje in st.session_state.messages:

    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# ============================================================
# 8. RECIBIR MENSAJES DEL USUARIO
# ============================================================

pregunta = st.chat_input(
    "Escribe tu pregunta aquÃ­..."
)

if pregunta:

    # Guardar pregunta
    st.session_state.messages.append(
        {
            "role": "user",
            "content": pregunta
        }
    )

    # Mostrar pregunta
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Generar respuesta
    with st.chat_message("assistant"):

        with st.spinner("Astra estÃ¡ pensando..."):

            try:

                respuesta = (
                    st.session_state.chat_session.send_message(
                        pregunta
                    )
                )

                texto_respuesta = respuesta.text

                if not texto_respuesta:
                    texto_respuesta = (
                        "No pude generar una respuesta. "
                        "Intenta nuevamente."
                    )

                st.markdown(texto_respuesta)

                # Guardar respuesta
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": texto_respuesta
                    }
                )

            except Exception as e:

                error = str(e)

                if "429" in error:
                    st.error(
                        "Se alcanzÃ³ el lÃ­mite de solicitudes "
                        "de Gemini. Intenta mÃ¡s tarde."
                    )

                elif "503" in error:
                    st.error(
                        "Gemini estÃ¡ temporalmente ocupado. "
                        "Intenta nuevamente."
                    )

                elif "404" in error:
                    st.error(
                        "El modelo seleccionado no estÃ¡ disponible. "
                        "Verifica el nombre del modelo."
                    )

                else:
                    st.error(
                        "OcurriÃ³ un error al consultar Gemini. "
                        "Revisa la terminal para mÃ¡s detalles."
                    )
                    print(f"Error de Gemini: {e}")

# ============================================================
# 9. PIE DE PÃGINA
# ============================================================

st.markdown("---")

st.caption(
    "Astra | AplicaciÃ³n desarrollada con "
    "Python, Streamlit y Google Gemini"
)

