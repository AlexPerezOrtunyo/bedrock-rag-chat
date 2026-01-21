import streamlit as st
import json
import os
import uuid
import time
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# --- 1. CARGA DE CREDENCIALES Y CONFIGURACIÓN AWS ---
load_dotenv()  # Carga las claves del archivo .env

AGENT_ID = "JS6SH9EWLM"          # Tu Agente
AGENT_ALIAS_ID = "TSTALIASID"    # Versión de prueba
REGION_NAME = "us-east-1"        # Región

# --- 2. FUNCIÓN PARA LLAMAR A AWS BEDROCK (EL CEREBRO) ---
def invoke_agent(prompt, session_id):
    """Conecta con AWS y obtiene la respuesta real del Agente"""
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
        return f"⚠️ Error de conexión con AWS: {e}"
    except Exception as e:
        return f"⚠️ Error inesperado: {e}"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="PAC - Asesoría Inmobiliaria", page_icon="🏠", layout="wide")

# --- DISEÑO UI PERSONALIZADO (BRANDING PAC) ---
st.markdown("""
    <style>
    /* Estilo global y fondo */
    .stApp { background-color: #ffffff; }
    
    /* 1. MENSAJES DEL USUARIO (AZUL PAC) */
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) {
        background-color: #f1f4f9; 
        border-right: 5px solid #1d355e;
        border-radius: 15px 0px 15px 15px;
        margin-left: 20%;
    }
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from user"]) div[data-testid="stChatMessageContent"] {
        color: #1d355e;
    }

    /* 2. MENSAJES DE LA IA (VERDE PAC) */
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) {
        background-color: #f2f8f2;
        border-left: 5px solid #48a44c;
        border-radius: 0px 15px 15px 15px;
        margin-right: 20%;
    }
    [data-testid="stChatMessage"]:has(div[aria-label="Chat message from assistant"]) div[data-testid="stChatMessageContent"] {
        color: #2e5d30;
    }

    /* Ajuste de iconos (Avatares) */
    [data-testid="stChatAvatarUser"] { background-color: #1d355e !important; }
    [data-testid="stChatAvatarAssistant"] { background-color: #48a44c !important; }

    /* Estilo del Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #e0e0e0; }

    /* Botones */
    div.stButton > button[kind="primary"] {
        background-color: #1d355e; color: white; border: none; font-weight: bold;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #48a44c; color: white;
    }
    
    /* Ocultar menú default de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS (HISTORIAL JSON) ---
FILE_PATH = "respaldo_conversaciones.json"

def cargar_datos():
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def guardar_datos():
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(st.session_state.chats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error guardando historial: {e}")

if "chats" not in st.session_state:
    st.session_state.chats = cargar_datos()

if "chat_actual" not in st.session_state:
    if st.session_state.chats:
        st.session_state.chat_actual = list(st.session_state.chats.keys())[0]
    else:
        st.session_state.chat_actual = None

def nueva_conversacion():
    nuevo_id = str(uuid.uuid4())
    st.session_state.chats[nuevo_id] = {
        "titulo": "Nueva Consulta PAC",
        "mensajes": [{"role": "assistant", "content": "Hola, soy tu asesor PAC experto en leyes e inversión. ¿En qué puedo ayudarte hoy?"}],
        "nombre_fijado": False
    }
    st.session_state.chat_actual = nuevo_id
    guardar_datos()

if not st.session_state.chats:
    nueva_conversacion()

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logoFoto.png", use_container_width=True)
    except:
        st.markdown("## 🏢 PAC INMOBILIARIA")
        st.caption("(Sube un archivo 'logoFoto.png' para ver el logo)")
    
    st.divider()
    if st.button(" ➕ Nueva Búsqueda", use_container_width=True, type="primary"):
        nueva_conversacion()
        st.rerun()
    
    st.markdown("### 📋 Historial")
    # Mostrar historial (limitado a últimos 10 para no saturar)
    chats_ordenados = list(st.session_state.chats.keys())[::-1][:10]
    
    for chat_id in chats_ordenados:
        col_c, col_d = st.columns([0.8, 0.2])
        with col_c:
            label = st.session_state.chats[chat_id]["titulo"]
            display_label = label if len(label) < 18 else label[:15] + "..."
            tipo = "primary" if st.session_state.chat_actual == chat_id else "secondary"
            if st.button(display_label, key=f"s_{chat_id}", use_container_width=True, type=tipo):
                st.session_state.chat_actual = chat_id
                st.rerun()
        with col_d:
            if st.button("🗑️", key=f"d_{chat_id}"):
                del st.session_state.chats[chat_id]
                # Si borramos el actual, reseteamos
                if st.session_state.chat_actual == chat_id:
                    st.session_state.chat_actual = list(st.session_state.chats.keys())[0] if st.session_state.chats else None
                    if not st.session_state.chat_actual: nueva_conversacion()
                guardar_datos()
                st.rerun()

# --- CHAT PRINCIPAL ---
chat_id = st.session_state.chat_actual
chat_data = st.session_state.chats[chat_id]

st.markdown(f"<h2 style='text-align: center;'>{chat_data['titulo']}</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #48a44c; font-size: 0.8rem;'>Conectado a AWS Bedrock Knowledge Base</p>", unsafe_allow_html=True)
st.divider()

# Renderizar mensajes anteriores
for message in chat_data["mensajes"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT Y LÓGICA DE RESPUESTA ---
if prompt := st.chat_input("Escribe tu consulta inmobiliaria..."):
    # 1. Fijar título si es el primer mensaje
    if not chat_data["nombre_fijado"]:
        chat_data["titulo"] = prompt[:30]
        chat_data["nombre_fijado"] = True

    # 2. Mostrar mensaje usuario
    chat_data["mensajes"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 3. LLAMADA A AWS (Aquí es donde ocurre la magia)
    with st.chat_message("assistant"):
        # Usamos st.status para un efecto de carga más moderno que el spinner
        with st.status("Consultando base de conocimientos...", expanded=False) as status:
            time.sleep(0.5) # Pequeña pausa estética
            
            # ---> LLAMADA REAL A TU AGENTE <---
            respuesta_aws = invoke_agent(prompt, chat_id)
            
            status.update(label="Respuesta generada", state="complete", expanded=False)
        
        # 4. Mostrar y guardar respuesta
        if respuesta_aws:
            st.write(respuesta_aws)
            chat_data["mensajes"].append({"role": "assistant", "content": respuesta_aws})
        else:
            st.error("No se recibió respuesta del agente.")

    # 5. Guardar en JSON
    guardar_datos()
    # Forzar recarga (opcional, en algunos casos ayuda a actualizar el sidebar)
    # st.rerun()