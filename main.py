import streamlit as st
from openai import OpenAI
import os
import PyPDF2

# === SETUP ===
st.set_page_config(page_title="memoriq.ai", layout="wide")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if "files" not in st.session_state:
    st.session_state["files"] = {}

# Memoriq-Header in der Sidebar
st.sidebar.markdown("<h1 style='text-align:center;'>Memoriq</h1>", unsafe_allow_html=True)

# Navigation als Radio-Buttons ohne Label (label hidden)
pages = ["Upload", "Meine Dateien", "Fragen"]
page = st.sidebar.radio(
    label="Navigation",
    options=pages,
    label_visibility="collapsed",  # Label ausblenden
)

# === SEITE 1: UPLOAD ===
if page == "Upload":
    st.title("Datei hochladen")
    uploaded_file = st.file_uploader("Lade eine Datei hoch", type=["pdf", "txt", "jpg", "png"])

    if uploaded_file is not None:
        file_name = uploaded_file.name

        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            content = "\n".join([page.extract_text() for page in pdf_reader.pages])
        elif uploaded_file.type.startswith("text/"):
            content = uploaded_file.getvalue().decode("utf-8")
        else:
            content = f"[{file_name}] (Dateityp {uploaded_file.type}) – noch nicht unterstützt"

        st.session_state["files"][file_name] = content
        st.success(f"✅ Datei '{file_name}' erfolgreich hochgeladen.")
        st.subheader("Inhalt (Auszug):")
        st.write(content[:500])

# === SEITE 2: MEINE DATEIEN ===
elif page == "Meine Dateien":
    st.title("Meine Dateien")
    if not st.session_state["files"]:
        st.info("Du hast noch keine Dateien hochgeladen.")
    else:
        for name, content in st.session_state["files"].items():
            with st.expander(f"{name}"):
                st.write(content[:500])
                if st.button(f"🗑 Löschen: {name}", key=f"delete_{name}"):
                    del st.session_state["files"][name]
                    st.experimental_rerun()

# === SEITE 3: FRAGEN ===
elif page == "Fragen":
    st.title("Frag deine Dateien")
    if not st.session_state["files"]:
        st.info("Bitte lade zuerst eine Datei hoch.")
    else:
        file_choice = st.selectbox("Wähle eine Datei", list(st.session_state["files"].keys()))
        query = st.text_input("Deine Frage")
        if query:
            context = st.session_state["files"][file_choice]
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Du bist ein persönlicher Wissensassistent."},
                        {"role": "user", "content": f"{context}\n\nFrage: {query}"}
                    ],
                    max_tokens=300
                )
                st.markdown("**Antwort:**")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Fehler bei der AI-Anfrage: {e}")
