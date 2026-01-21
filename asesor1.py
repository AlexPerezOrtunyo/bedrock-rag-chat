import streamlit as st
import json
import os
import uuid

# --- CONFIGURACIÓN Y PERSISTENCIA ---
FILE_PATH = "respaldo_conversaciones.json"

def cargar_datos():
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_datos():
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(st.session_state.chats, f, ensure_ascii=False, indent=4)

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asesor Inmobiliario AI", page_icon="🏠", layout="wide")

# --- INICIALIZACIÓN DEL ESTADO ---
if "chats" not in st.session_state:
    st.session_state.chats = cargar_datos()

if "chat_actual" not in st.session_state:
    if st.session_state.chats:
        st.session_state.chat_actual = list(st.session_state.chats.keys())[0]
    else:
        st.session_state.chat_actual = None

# --- FUNCIÓN PARA CREAR NUEVO CHAT ---
def nueva_conversacion():
    nuevo_id = str(uuid.uuid4())
    st.session_state.chats[nuevo_id] = {
        "titulo": "Nueva Consulta",
        "mensajes": [{"role": "assistant", "content": "¡Hola! Soy tu asesor inmobiliario. ¿En qué puedo ayudarte?"}],
        "nombre_fijado": False
    }
    st.session_state.chat_actual = nuevo_id
    guardar_datos()

# Crear chat inicial si la base de datos está vacía
if not st.session_state.chats:
    nueva_conversacion()

## --- SIDEBAR: HISTORIAL PERMANENTE ---
with st.sidebar:
    st.title("📂 Mis Conversaciones")
    
    if st.button("➕ Nueva Consulta", use_container_width=True):
        nueva_conversacion()
        st.rerun()
    
    st.divider()
    
    # Listado de chats desde el archivo cargado
    for chat_id in list(st.session_state.chats.keys()):
        col_chat, col_del = st.columns([0.8, 0.2])
        
        with col_chat:
            label = st.session_state.chats[chat_id]["titulo"]
            display_label = (label[:25] + '...') if len(label) > 25 else label
            
            # Estilo diferente para el chat activo
            type_button = "primary" if st.session_state.chat_actual == chat_id else "secondary"
            if st.button(display_label, key=f"sel_{chat_id}", use_container_width=True, type=type_button):
                st.session_state.chat_actual = chat_id
                st.rerun()
        
        with col_del:
            if st.button("🗑️", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                guardar_datos()
                if st.session_state.chat_actual == chat_id:
                    st.session_state.chat_actual = next(iter(st.session_state.chats)) if st.session_state.chats else None
                if not st.session_state.chats:
                    nueva_conversacion()
                st.rerun()

## --- CUERPO PRINCIPAL ---
chat_id = st.session_state.chat_actual
chat_data = st.session_state.chats[chat_id]

st.title(f"🏠 {chat_data['titulo']}")

# Mostrar mensajes
for message in chat_data["mensajes"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat
if prompt := st.chat_input("Escribe aquí tu consulta inmobiliaria..."):
    # 1. Cambiar título automáticamente con el primer mensaje
    if not chat_data["nombre_fijado"]:
        chat_data["titulo"] = prompt
        chat_data["nombre_fijado"] = True

    # 2. Guardar mensaje del usuario
    chat_data["mensajes"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Respuesta del Asesor
    with st.chat_message("assistant"):
        respuesta = f"Entendido. Como tu asesor inmobiliario, estoy procesando tu solicitud: '{prompt}'."
        st.markdown(respuesta)
        chat_data["mensajes"].append({"role": "assistant", "content": respuesta})
    
    # 4. GUARDAR EN DISCO (JSON)
    guardar_datos()
    st.rerun()