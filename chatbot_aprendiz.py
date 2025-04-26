import streamlit as st
import json
import os
import random

# --- Cargar conocimiento desde archivo ---
CONOCIMIENTO_PATH = "conocimiento.json"

def cargar_conocimiento():
    if os.path.exists(CONOCIMIENTO_PATH):
        with open(CONOCIMIENTO_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return {
            "respuestas_bot": {},
            "preguntas_al_usuario": []
        }

def guardar_conocimiento():
    with open(CONOCIMIENTO_PATH, "w", encoding="utf-8") as file:
        json.dump(conocimiento, file, ensure_ascii=False, indent=2)

# --- Simulación de backup a GitHub ---
def hacer_backup_en_github():
    st.success("✅ Backup en GitHub simulado. (Agrega tu integración real aquí)")

# --- Interfaz de la app ---
st.set_page_config(page_title="Chatbot Explorador", page_icon="🤖")
st.title("🤖 Chatbot de Bienvenida")
st.write("Haz una pregunta o responde a las preguntas del bot.")

# --- Carga inicial de datos ---
conocimiento = cargar_conocimiento()

# --- Entrada del usuario ---
entrada_usuario = st.text_input("Tú:", "")

if st.button("Enviar") and entrada_usuario.strip():
    entrada = entrada_usuario.strip()

    # Mostrar respuesta si la pregunta está registrada
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
        st.success("✅ ¡Gracias por tu respuesta!")
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
