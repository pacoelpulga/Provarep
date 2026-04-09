import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Multi-Progetto")

FILE_PATH = "tasks.csv"

# ===== LOAD =====
if "tasks" not in st.session_state:
    if os.path.exists(FILE_PATH):
        st.session_state.tasks = pd.read_csv(FILE_PATH).to_dict("records")
    else:
        st.session_state.tasks = []

def save_tasks():
    pd.DataFrame(st.session_state.tasks).to_csv(FILE_PATH, index=False)

# ===== INPUT =====
st.subheader("➕ Nuovo Task")

col1, col2 = st.columns(2)

with col1:
    project = st.text_input("Progetto")
    name = st.text_input("Nome Task")
    description = st.text_area("Descrizione")
    color = st.color_picker("Colore Task", "#1f77b4")

with col2:
    start = st.date_input("Inizio")
    end = st.date_input("Fine")

if st.button("Aggiungi Task"):
    if not project or not name:
        st.error("Compila almeno progetto e nome task")
    elif end < start:
        st.error("Date non valide")
    else:
        st.session_state.tasks.append({
            "Progetto": project,
            "Task": name,
            "Descrizione": description,
            "Start": str(start),
            "End": str(end),
            "Colore": color
        })
        save_tasks()
        st.success("Task aggiunto!")

# ===== DATA =====
if st.session_state.tasks:

    df = pd.DataFrame(st.session_state.tasks)

    # colonne mancanti
    for col in ["Descrizione", "Colore"]:
        if col not in df.columns:
            df[col] = ""

    # conversione sicura
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")

    df = df.dropna(subset=["Start", "End"])

    # label asse Y
    df["Label"] = df["Task"] + " | " + df["Descrizione"]

    # ===== EDITOR (semplice e stabile) =====
    st.subheader("📋 Modifica Task")

    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.session_state.tasks = edited_df.to_dict("records")
    save_tasks()

    df = pd.DataFrame(st.session_state.tasks)
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")
    df = df.dropna(subset=["Start", "End"])

    df["Label"] = df["Task"] + " | " + df["Descrizione"]

    # ===== GANTT =====
    if len(df) > 0:

        st.subheader("📊 Diagramma di Gantt")

        # fine inclusiva
        df["End"] = df["End"] + pd.Timedelta(days=1)

        # colori sicuri
        color_map = {
            row["Label"]: row["Colore"] if row["Colore"] else "#1f77b4"
            for _, row in df.iterrows()
        }

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="End",
            y="Label",
            color="Label",
            color_discrete_map=color_map,
            hover_data=["Task", "Descrizione"]
        )

        fig.update_yaxes(autorange="reversed", title=None)

        # asse tempo stabile
        fig.update_xaxes(
            tickformat="%d/%m",
            dtick="D1",
            showgrid=True
        )

        # ===== LINEA OGGI =====
        today = datetime.now()
        fig.add_vline(
            x=today,
            line_width=3,
            line_color="red"
        )

        # ===== DOMENICHE (ottimizzato) =====
        start_range = df["Start"].min().date()
        end_range = df["End"].max().date()

        sundays = pd.date_range(start=start_range, end=end_range, freq="W-SUN")

        for d in sundays:
            fig.add_vrect(
                x0=d,
                x1=d + timedelta(days=1),
                fillcolor="lightgrey",
                opacity=0.2,
                layer="below",
                line_width=0,
            )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nessun task inserito")
