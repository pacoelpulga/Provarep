import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Multi-Progetto")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.subheader("➕ Nuovo Task")

project = st.text_input("Progetto")
name = st.text_input("Nome Task")
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
        st.success("Aggiunto!")

if st.session_state.tasks:

    df = pd.DataFrame(st.session_state.tasks)

    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

    st.subheader("📋 Task")
    st.dataframe(df, use_container_width=True)

    projects = df["Progetto"].unique()
    selected = st.multiselect("Progetti", projects, default=projects)

    df = df[df["Progetto"].isin(selected)]

    if len(df) > 0:

        st.subheader("📊 Gantt")

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="End",
            y="Task",
            color="Progetto"
        )

        fig.update_xaxes(tickformat="%d/%m/%Y")
        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nessun task inserito")
