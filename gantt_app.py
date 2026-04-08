import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random

st.set_page_config(page_title="Gantt Pro", layout="wide")

st.title("📊 Gantt Pro Multi-Progetto")

# ===== STATE =====
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ===== SIDEBAR =====
st.sidebar.header("➕ Nuovo Task")

project = st.sidebar.text_input("Progetto")
name = st.sidebar.text_input("Nome Task")
category = st.sidebar.selectbox("Categoria", ["Lavoro", "Studio", "Altro"])

start = st.sidebar.datetime_input("Inizio")
end = st.sidebar.datetime_input("Fine")

# lista task esistenti per dipendenze
existing_tasks = [t["Task"] for t in st.session_state.tasks]
dependency = st.sidebar.selectbox("Dipende da", ["Nessuno"] + existing_tasks)

if st.sidebar.button("Aggiungi"):
    if not project.strip():
        st.sidebar.error("Inserisci progetto")
    elif not name.strip():
        st.sidebar.error("Inserisci nome task")
    elif end < start:
        st.sidebar.error("Date non valide")
    else:
        st.session_state.tasks.append({
            "Progetto": project,
            "Task": name,
            "Categoria": category,
            "Start": start,
            "End": end,
            "Dipende_da": None if dependency == "Nessuno" else dependency
        })
        st.sidebar.success("Aggiunto!")

# ===== DATA =====
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)

    st.subheader("📋 Modifica Task")
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    st.session_state.tasks = edited_df.to_dict("records")

    # ===== FILTRO PROGETTI =====
    projects = edited_df["Progetto"].unique().tolist()
    selected_projects = st.multiselect("🎯 Progetti", projects, default=projects)

    df = edited_df[edited_df["Progetto"].isin(selected_projects)]

    # ===== CONTROLLO DIPENDENZE =====
    st.subheader("🔗 Controllo Dipendenze")

    errors = []
    task_names = df["Task"].tolist()

    for _, row in df.iterrows():
        dep = row.get("Dipende_da")
        if dep and dep not in task_names:
            errors.append(f"{row['Task']} dipende da '{dep}' (non esiste)")

    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("Dipendenze OK")

    # ===== GANTT =====
    if st.button("📊 Genera Gantt"):
        fig, ax = plt.subplots(figsize=(12, 6))

        color_map = {}
        for p in df["Progetto"].unique():
            color_map[p] = (random.random(), random.random(), random.random())

        y = 0
        y_labels = []
        y_pos = {}

        # ordinamento per progetto
        for project in df["Progetto"].unique():
            proj_df = df[df["Progetto"] == project]

            for _, row in proj_df.iterrows():
                duration = (row["End"] - row["Start"]).total_seconds() / 3600

                ax.barh(
                    y,
                    duration,
                    left=row["Start"],
                    color=color_map[project]
                )

                label = f"{project} | {row['Task']}"
                y_labels.append(label)
                y_pos[row["Task"]] = y
                y += 1

            y += 1  # spazio tra progetti

        # ===== DISEGNO DIPENDENZE =====
        for _, row in df.iterrows():
            dep = row.get("Dipende_da")
            if dep and dep in y_pos:
                y1 = y_pos[dep]
                y2 = y_pos[row["Task"]]

                x1 = df[df["Task"] == dep]["End"].values[0]
                x2 = row["Start"]

                ax.plot([x1, x2], [y1, y2], linestyle="dashed")

        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels)

        ax.set_title("Gantt Pro con Dipendenze")
        ax.set_xlabel("Tempo")

        plt.xticks(rotation=45)
        st.pyplot(fig)

        # export PNG
        fig.savefig("gantt_pro.png")
        with open("gantt_pro.png", "rb") as f:
            st.download_button("⬇️ Scarica PNG", f, "gantt_pro.png")

    # ===== EXPORT CSV =====
    csv = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Scarica CSV", csv, "tasks_pro.csv")

    # ===== IMPORT CSV =====
    uploaded = st.file_uploader("📂 Carica CSV")
    if uploaded:
        df_loaded = pd.read_csv(uploaded)
        st.session_state.tasks = df_loaded.to_dict("records")
        st.success("Caricato!")
        st.rerun()

else:
    st.info("Nessun task inserito")
