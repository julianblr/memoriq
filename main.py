import streamlit as st
from openai import OpenAI
import os

st.title("memoriq.ai - Dein AI Wissensassistent")

# OpenAI API Key aus den Secrets lesen
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

uploaded_file = st.file_uploader("Lade eine Datei hoch (PDF, Text, Bild)", type=["pdf", "txt", "png", "jpg", "jpeg"])
file_content = None

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        file_content = ""
        for page in pdf_reader.pages:
            file_content += page.extract_text() + "\n"
    elif uploaded_file.type.startswith("text/"):
        file_content = uploaded_file.getvalue().decode("utf-8")
    else:
        file_content = f"Dateityp {uploaded_file.type} wird aktuell nicht unterstützt."

    st.write("Inhalt der Datei (Auszug):")
    st.write(file_content[:500])  # Zeige die ersten 500 Zeichen

query = st.text_input("Stelle eine Frage an Deinen Assistenten")

if query:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": (file_content or "") + "\n" + query}],
            max_tokens=150
        )
        answer = response.choices[0].message.content
        st.write(answer)
    except Exception as e:
        st.error(f"Fehler bei der AI-Anfrage: {e}")
