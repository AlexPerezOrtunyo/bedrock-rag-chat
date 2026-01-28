import streamlit as st
import json
import os
import uuid
import time
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import pandas as pd

# --------------------------------------------------
# 1. CARGA DE CREDENCIALES Y CONFIGURACIÓN AWS
# --------------------------------------------------
load_dotenv()

AGENT_ID = "JS6SH9EWLM"
AGENT_ALIAS_ID = "TSTALIASID"
REGION_NAME = "us-east-1"

# --------------------------------------------------
# 2. FUNCIÓN PARA LLAMAR A AWS BEDROCK
# --------------------------------------------------
def invoke_agent(prompt, session_id):
    client = boto3.client("bedrock-agent-runtime", region_name=REGION_NAME)
    try:
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=prompt
        )
        completion = ""
        for event in response.get("completion"):
            chunk = event["chunk"]
            if chunk:
                completion += chunk["bytes"].decode("utf-8")
        return completion
    except ClientError as e:
        return f"⚠️ Error AWS: {e}"
    except Exception as e:
        return f"⚠️ Error inesperado: {e}"

# --------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------
st.set_page_config(
    page_title="PAC - Asesoría Inmobiliaria",
    page_icon="🏠",
    layout="wide"
)

# --------------------------------------------------
# ESTILOS
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #ffffff; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HISTORIAL JSON
# --------------------------------------------------
FILE_PATH = "respaldo_conversaciones.json"

def cargar_datos():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(st.session_state.chats, f, ensure_ascii=False, indent=4)

# --------------------------------------------------
# MÉTRICAS DASHBOARD
# --------------------------------------------------
def obtener_metricas(chats):
    total_chats = len(chats)
    total_mensajes = 0
    mensajes_usuario = 0
    mensajes_ia = 0

    for chat in chats.values():
        total_mensajes += len(chat["mensajes"])
        for msg in chat["mensajes"]:
            if msg["role"] == "user":
                mensajes_usuario += 1
            else:
                mensajes_ia += 1

    return total_chats, total_mensajes, mensajes_usuario, mensajes_ia

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "chats" not in st.session_state:
    st.session_state.chats = cargar_datos()

if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = None

def nueva_conversacion():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "titulo": "Nueva Consulta PAC",
        "mensajes": [
            {"role": "assistant", "content": "Hola, soy tu asesor PAC. ¿En qué puedo ayudarte?"}
        ],
        "nombre_fijado": False
    }
    st.session_state.chat_actual = chat_id
    guardar_datos()

if not st.session_state.chats:
    nueva_conversacion()

if not st.session_state.chat_actual:
    st.session_state.chat_actual = list(st.session_state.chats.keys())[0]

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    try:
        st.image("logoFoto.png", use_container_width=True)
    except:
        st.markdown("## 🏢 PAC INMOBILIARIA")

    st.divider()

    # NUEVA BÚSQUEDA
    if st.button("➕ Nueva Búsqueda", type="primary", use_container_width=True):
        nueva_conversacion()
        st.rerun()

    # DASHBOARD
    st.markdown("### 📊 Dashboard")
    total_chats, total_mensajes, user_msgs, ia_msgs = obtener_metricas(st.session_state.chats)

    col1, col2 = st.columns(2)
    col1.metric("💬 Chats", total_chats)
    col2.metric("🧠 Mensajes", total_mensajes)

    col3, col4 = st.columns(2)
    col3.metric("👤 Usuario", user_msgs)
    col4.metric("🤖 IA", ia_msgs)

    st.caption("🟢 Conectado a AWS Bedrock")
    st.divider()

    # BUSCADOR
    st.markdown("### 🔍 Buscar Conversaciones")
    busqueda = st.text_input("Buscar", placeholder="alquiler, ley, inversión...")

    # HISTORIAL CON BOTONES BORRAR
    st.markdown("### 📋 Historial")
    chats_filtrados = [chat_id for chat_id, chat in st.session_state.chats.items()
                       if busqueda.lower() in st.session_state.chats[chat_id]["titulo"].lower()]

    for chat_id in chats_filtrados[::-1][:10]:
        chat = st.session_state.chats[chat_id]
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            if st.button(chat["titulo"][:20], key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.chat_actual = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.chat_actual == chat_id:
                    st.session_state.chat_actual = None
                guardar_datos()
                st.rerun()

# --------------------------------------------------
# CHAT PRINCIPAL
# --------------------------------------------------
chat_id = st.session_state.chat_actual
chat_data = st.session_state.chats[chat_id]

st.markdown(f"## {chat_data['titulo']}")
st.caption("🏠 Asesoría inmobiliaria inteligente")

for msg in chat_data["mensajes"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu consulta inmobiliaria..."):
    if not chat_data["nombre_fijado"]:
        chat_data["titulo"] = prompt[:30]
        chat_data["nombre_fijado"] = True

    chat_data["mensajes"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Consultando PAC...", expanded=False):
            respuesta = invoke_agent(prompt, chat_id)
        st.markdown(respuesta)
        chat_data["mensajes"].append({"role": "assistant", "content": respuesta})

    guardar_datos()
