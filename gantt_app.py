import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Multi-Progetto")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

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
        st.success("Task aggiunto!")

# ===== DATA =====
if st.session_state.tasks:

    df = pd.DataFrame(st.session_state.tasks)

    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    # ===== EDIT =====
    st.subheader("📋 Modifica Task")

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic"
    )

    st.session_state.tasks = edited_df.to_dict("records")

    # reload
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

        # fix barre invisibili
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
