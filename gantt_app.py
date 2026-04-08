import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Multi-Progetto")

FILE_PATH = "tasks.csv"

# ===== LOAD DATA =====
if "tasks" not in st.session_state:
    if os.path.exists(FILE_PATH):
        st.session_state.tasks = pd.read_csv(FILE_PATH).to_dict("records")
    else:
        st.session_state.tasks = []

# ===== SAVE FUNCTION =====
def save_tasks():
    pd.DataFrame(st.session_state.tasks).to_csv(FILE_PATH, index=False)

# ===== INPUT =====
st.subheader("➕ Nuovo Task")

col1, col2 = st.columns(2)

with col1:
    project = st.text_input("Progetto")
    name = st.text_input("Nome Task")

with col2:
    start = st.date_input("Inizio")
    end = st.date_input("Fine")

if st.button("Aggiungi Task"):
    if not project or not name:
        st.error("Compila tutti i campi")
    elif end < start:
        st.error("Date non valide")
    else:
        st.session_state.tasks.append({
            "Progetto": project,
            "Task": name,
            "Start": str(start),
            "End": str(end)
        })
        save_tasks()
        st.success("Task aggiunto!")

# ===== DATA =====
if st.session_state.tasks:

    df = pd.DataFrame(st.session_state.tasks)

    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    # 👉 SOLO giorno/mese per visualizzazione
    df_display = df.copy()
    df_display["Start"] = df_display["Start"].dt.strftime("%d/%m")
    df_display["End"] = df_display["End"].dt.strftime("%d/%m")

    # ===== EDIT =====
    st.subheader("📋 Modifica Task")

    edited_df = st.data_editor(
        df_display,
        use_container_width=True,
        num_rows="dynamic"
    )

    # 👉 riconversione date dopo editing
    try:
        edited_df["Start"] = pd.to_datetime(edited_df["Start"], format="%d/%m")
        edited_df["End"] = pd.to_datetime(edited_df["End"], format="%d/%m")
    except:
        pass

    st.session_state.tasks = edited_df.to_dict("records")
    save_tasks()

    # reload corretto
    df = pd.DataFrame(st.session_state.tasks)
    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    # ===== FILTER =====
    projects = df["Progetto"].unique()
    selected = st.multiselect("Seleziona Progetti", projects, default=projects)

    df = df[df["Progetto"].isin(selected)]

    # ===== GANTT =====
    if len(df) > 0:

        st.subheader("📊 Diagramma di Gantt")

        # fine inclusiva
        df["End"] = df["End"] + pd.Timedelta(days=1)

        # evita barre invisibili
        df.loc[df["End"] <= df["Start"], "End"] = df["Start"] + pd.Timedelta(days=1)

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="End",
            y="Task",
            color="Progetto"
        )

        fig.update_yaxes(autorange="reversed")

        fig.update_xaxes(
            tickformat="%d",
            dtick="D1",
            showgrid=True
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nessun task inserito")
