import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Chave de Lutas", layout="wide")

# ✅ TÍTULO CENTRAL
st.markdown("<h1 style='text-align: center; font-size: 52px; margin-top: 10px;'>UAEW Fightweek Tasks</h1>", unsafe_allow_html=True)

# 🔁 Atualização automática
st_autorefresh(interval=10000, key="auto_refresh")

# 📄 CSV do Google Sheets
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRih5bZ-W7jgTsXbjE7mWpOQe8JeV4dQbMVH4gv9qhhkOc4NdKf-wXdRp7xwUtzZb8FqniMUt3VlXu-/pub?gid=330897584&single=true&output=csv"

# 📥 Carrega os dados
df = pd.read_csv(url)

# Atualiza nome da coluna de imagem
df.rename(columns={"PHOTO": "PHOTO1"}, inplace=True)

if {"PHOTO1", "CORNER", "FIGHT N", "EVENT"}.issubset(df.columns):
    df = df[df["PHOTO1"].astype(str).str.startswith("http", na=False)].copy()
    df.fillna("", inplace=True)
    df["FIGHT N"] = df["FIGHT N"].astype(str).str.zfill(2)
    df = df.sort_values(by=["EVENT", "FIGHT N", "CORNER"])

    # 🎨 CSS
    st.markdown("""
    <style>
    .fight-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        margin-bottom: 40px;
    }
    .card {
        background-color: #e0e0e0;
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px 20px;
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 6px;
        width: 100%;
        position: relative;
    }
    .card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        height: 6px;
        width: 100%;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }
    .blue-corner .card::before {
        background-color: #007BFF;
    }
    .red-corner .card::before {
        background-color: #DC3545;
    }
    .card-body {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 25px;
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
        font-size: 26px;
        font-weight: 800;
        color: #000;
        margin: 0 0 4px 0;
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
        font-size: 48px;
        font-weight: 900;
        color: #999999;
        text-align: center;
        min-width: 140px;
    }
    .event-title {
        font-size: 38px;
        font-weight: 800;
        text-align: center;
        margin: 30px 0 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    def status_tag(valor, label):
        estado = str(valor).strip().lower()
        if estado == "pending":
            return f"<div class='pending'>{label}</div>"
        elif estado == "done":
            return f"<div class='done'>{label}</div>"
        return ""

    def render_card(row):
        foto = f"<img src='{row['PHOTO1']}' width='80'>"
        nome = f"<div class='athlete-name'>{row.get('NAME', '')}</div>"
        status_html = "".join([
            status_tag(row.get('BLACK SCREEN\nVIDEO', ''), "BLACK SCREEN"),
            status_tag(row.get('PHOTOSHOOT', ''), "PHOTOSHOOT"),
            status_tag(row.get('BLOOD\nTEST', ''), "BLOOD TEST"),
            status_tag(row.get('UNIFORM', ''), "UNIFORM"),
            status_tag(row.get('MUSIC', ''), "MUSIC"),
            status_tag(row.get('STATS', ''), "STATS")
        ])
        chegada = row.get("ARRIVAL", "")
        corner_class = "blue-corner" if row.get("CORNER", "").upper() == "BLUE" else "red-corner"
        return f"""
        <div class='{corner_class}'>
            <div class='card'>
                <div class='card-body'>
                    {foto}
                    <div class='info-block'>
                        {nome}
                        <div class='status-row'>{status_html}</div>
                        <div class='arrival-info'>{chegada}</div>
                    </div>
                </div>
            </div>
        </div>
        """

    for evento, grupo_evento in df.groupby("EVENT"):
        st.markdown(f"<div class='event-title'>{evento}</div>", unsafe_allow_html=True)

        for luta, luta_df in grupo_evento.groupby("FIGHT N"):
            blue = luta_df[luta_df["CORNER"].str.upper() == "BLUE"]
            red = luta_df[luta_df["CORNER"].str.upper() == "RED"]

            st.markdown("<div class='fight-line'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([5, 2, 5])

            with col1:
                st.markdown(render_card(blue.iloc[0]) if not blue.empty else "🟦 Sem atleta no corner BLUE", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='fight-number'>{luta}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(render_card(red.iloc[0]) if not red.empty else "🔴 Sem atleta no corner RED", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.error("❌ Faltam colunas obrigatórias: 'PHOTO1', 'CORNER', 'FIGHT N', 'EVENT'")
