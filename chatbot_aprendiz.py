import streamlit as st
import json
import os
import random
import requests
import base64
from datetime import datetime, timezone

# --- Ruta del archivo de conocimiento ---
CONOCIMIENTO_PATH = "conocimiento.json"

# --- Función para obtener estado del último backup ---
def obtener_estado_backup(ruta_archivo="conocimiento.json"):
    url = "https://api.github.com/repos/LuizBN2/chatbot_ai_25/commits"
    params = {"path": ruta_archivo, "per_page": 1}
    respuesta = requests.get(url, params=params)

    if respuesta.status_code == 200 and len(respuesta.json()) > 0:
        fecha_iso = respuesta.json()[0]["commit"]["committer"]["date"]
        fecha_commit = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
        ahora = datetime.now(timezone.utc)
        diferencia = (ahora - fecha_commit).total_seconds()

        if diferencia < 90:
            estado = "✅ Backup actualizado recientemente"
        else:
            estado = "⏳ Backup pendiente o retrasado"

        fecha_formateada = fecha_commit.strftime("%d/%m/%Y %H:%M:%S")
        return estado, fecha_formateada
    else:
        return "⚠️ No se pudo obtener el estado del backup", "No disponible"

# --- Función para cargar el conocimiento ---
def cargar_conocimiento():
    if os.path.exists(CONOCIMIENTO_PATH):
        with open(CONOCIMIENTO_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {
            "respuestas_bot": {},
            "preguntas_al_usuario": []
        }

# --- Guardar conocimiento localmente ---
def guardar_conocimiento():
    with open(CONOCIMIENTO_PATH, "w", encoding="utf-8") as file:
        json.dump(conocimiento, file, ensure_ascii=False, indent=2)

# --- Hacer backup real en GitHub usando API ---
def hacer_backup_en_github():
    token = os.getenv("GH_TOKEN")
    if not token:
        st.error("❌ Token de GitHub no disponible en el entorno.")
        return

    repo = "LuizBN2/chatbot_ai_25"
    path = "conocimiento.json"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    with open(CONOCIMIENTO_PATH, "rb") as file:
        contenido = file.read()
    contenido_base64 = base64.b64encode(contenido).decode("utf-8")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_resp = requests.get(url, headers=headers)
    sha = get_resp.json().get("sha") if get_resp.status_code == 200 else None

    payload = {
        "message": "🔄 Backup desde Streamlit",
        "content": contenido_base64,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        st.success("✅ Backup realizado exitosamente en GitHub.")
    else:
        st.error(f"❌ Error al hacer backup: {resp.status_code}")
        st.text(resp.text)

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Chatbot Explorador", page_icon="🤖")
st.title("🤖 Chatbot de Bienvenida")
st.write("Haz una pregunta o responde a las preguntas del bot.")

# --- Cargar conocimiento ---
conocimiento = cargar_conocimiento()

# --- Entrada del usuario ---
entrada_usuario = st.text_input("Tú:", "")

if st.button("Enviar") and entrada_usuario.strip():
    entrada = entrada_usuario.strip()

    if entrada in conocimiento["respuestas_bot"]:
        st.markdown(f"🤖 {conocimiento['respuestas_bot'][entrada]}")
    else:
        st.info("🤖 No tengo respuesta para eso todavía. ¿Quieres enseñarme?")
        nueva_respuesta = st.text_input("Escribe la respuesta que debería dar el bot:")
        if st.button("Guardar nueva respuesta") and nueva_respuesta.strip():
            conocimiento["respuestas_bot"][entrada] = nueva_respuesta.strip()
            guardar_conocimiento()
            st.success("✅ ¡Gracias! El bot ha aprendido esta respuesta.")

# --- Pregunta aleatoria del bot al usuario ---
st.markdown("---")
st.subheader("👁️ Pregunta del bot para ti")

if conocimiento["preguntas_al_usuario"]:
    pregunta = random.choice(conocimiento["preguntas_al_usuario"])
    st.info(f"🤖 El bot quiere saber: **{pregunta}**")
    respuesta = st.text_input("Tu respuesta:", key="respuesta_usuario")
    
    if st.button("Guardar respuesta del usuario"):
        if "respuestas_de_usuarios" not in conocimiento:
            conocimiento["respuestas_de_usuarios"] = {}
        
        if pregunta not in conocimiento["respuestas_de_usuarios"]:
            conocimiento["respuestas_de_usuarios"][pregunta] = []
        
        if respuesta.strip():
            conocimiento["respuestas_de_usuarios"][pregunta].append(respuesta.strip())
            guardar_conocimiento()
            st.success("✅ ¡Gracias! Tu respuesta ha sido guardada.")
else:
    st.warning("⚠️ El bot aún no tiene preguntas para hacerte.")


# --- Agregar nueva pregunta del bot ---
st.markdown("---")
st.subheader("➕ Agregar pregunta del bot para el usuario")

nueva_pregunta = st.text_input("Escribe una nueva pregunta que el bot hará al usuario:")

if st.button("Agregar pregunta") and nueva_pregunta.strip():
    conocimiento["preguntas_al_usuario"].append(nueva_pregunta.strip())
    guardar_conocimiento()
    st.success("✅ Pregunta agregada al bot.")

# --- Backup manual ---
st.markdown("---")
if st.button("📤 Hacer backup en GitHub"):
    guardar_conocimiento()
    hacer_backup_en_github()

# --- Estado del backup ---
st.markdown("---")
st.subheader("📦 Estado del backup automático")
estado, fecha = obtener_estado_backup()
st.info(f"{estado}\n\nÚltimo backup: **{fecha}**")
