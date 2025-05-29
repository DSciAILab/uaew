import streamlit as st
st.set_page_config(page_title="Chave de Lutas", layout="wide")

import pandas as pd
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# 🔁 Atualiza a página automaticamente a cada 10 segundos
st_autorefresh(interval=10000, key="auto_refresh")

# 📊 CSV do Google Sheets
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRih5bZ-W7jgTsXbjE7mWpOQe8JeV4dQbMVH4gv9qhhkOc4NdKf-wXdRp7xwUtzZb8FqniMUt3VlXu-/pub?gid=330897584&single=true&output=csv"
df = pd.read_csv(url)

if {"PHOTO1", "CORNER", "FIGHT N", "EVENT"}.issubset(df.columns):
    df = df[df["PHOTO1"].astype(str).str.startswith("http", na=False)].copy()
    df.fillna("", inplace=True)
    df["FIGHT N"] = df["FIGHT N"].astype(str).str.zfill(2)
    df = df.sort_values(by=["EVENT", "FIGHT N", "CORNER"])

    # 🎨 CSS Customizado
    st.markdown("""
    <style>
    .event-title {
        font-size: 38px;
        font-weight: 800;
        text-align: center;
        margin: 30px 0 10px 0;
    }
    .fight-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        margin-bottom: 40px;
    }
    .card {
        background-color: #f9f9f9;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 25px;
        width: 100%;
    }
    .card img {
        border-radius: 8px;
    }
    .info-block {
        display: flex;
        flex-direction: column;
    }
    .status-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 4px;
    }
    .arrival-info {
        font-size: 14px;
        font-weight: 500;
        color: #555;
        white-space: nowrap;
    }
    .athlete-name {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .pending {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 13px;
    }
    .done {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 13px;
    }
    .fight-number {
        font-size: 32px;
        font-weight: 800;
        color: #b30000;
        text-align: center;
        min-width: 140px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 🧩 Tags de Status
    def status_tag(valor, label):
        estado = str(valor).strip().lower()
        if estado == "pending":
            return f"<div class='pending'>{label}</div>"
        elif estado == "done":
            return f"<div class='done'>{label}</div>"
        return ""

    # 🧱 Card do atleta
    def render_card(row):
        foto = f"<img src='{row['PHOTO1']}' width='80'>"
        nome = f"<div class='athlete-name'>{row.get('NAME', '')}</div>"
        status_html = "".join([
            status_tag(row.get('PHOTOSHOOT', ''), "PHOTOSHOOT"),
            status_tag(row.get('UNIFORM', ''), "UNIFORM"),
            status_tag(row.get('MUSIC', ''), "MUSIC"),
            status_tag(row.get('STATS', ''), "STATS")
        ])
        chegada = row.get("ARRIVAL", "")
        return f"""
        <div class='card'>
            {foto}
            <div class='info-block'>
                {nome}
                <div class='status-row'>{status_html}</div>
            </div>
            <div class='arrival-info'>{chegada}</div>
        </div>
        """

    # 📦 Loop por Evento e Lutas
    for evento, grupo_evento in df.groupby("EVENT"):
        st.markdown(f"<div class='event-title'>🎯 Evento: {evento}</div>", unsafe_allow_html=True)

        for luta, luta_df in grupo_evento.groupby("FIGHT N"):
            blue = luta_df[luta_df["CORNER"].str.upper() == "BLUE"]
            red = luta_df[luta_df["CORNER"].str.upper() == "RED"]

            st.markdown("<div class='fight-line'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([5, 2, 5])

            with col1:
                st.markdown(render_card(blue.iloc[0]) if not blue.empty else "🟦 Sem atleta no corner BLUE", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='fight-number'>🥊<br>Luta {luta}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(render_card(red.iloc[0]) if not red.empty else "🔴 Sem atleta no corner RED", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("❌ Faltam colunas obrigatórias: 'PHOTO1', 'CORNER', 'FIGHT N', 'EVENT'")

