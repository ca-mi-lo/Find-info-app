import streamlit as st

st.title("Find info App")

st.text_input("¿Qué información estás buscando en el texto?", key="subject")

st.session_state.subject
