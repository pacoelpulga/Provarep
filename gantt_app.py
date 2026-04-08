import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Multi-Progetto")

# ===== SESSION STATE =====
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ===== INPUT NUOVO TASK =====
st.subheader("➕ Nuovo Task")

col1, col2 = st.columns(2)

with col1:
    project = st.text_input("Progetto")
        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nessun task inserito")
