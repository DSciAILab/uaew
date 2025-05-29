import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Configuração da página
st.set_page_config(page_title="UAEW Fightweek Tasks", layout="wide")

# Atualiza a página automaticamente a cada 10 segundos
st_autorefresh(interval=10000, key="auto_refresh")

# CSV do Google Sheets
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRih5bZ-W7jgTsXbjE7mWpOQe8JeV4dQbMVH4gv9qhhkOc4NdKf-wXdRp7xwUtzZb8FqniMUt3VlXu-/pub?gid=330897584&single=true&output=csv"
df = pd.read_csv(url)

# Sidebar para seleção da página
pagina = st.sidebar.radio("Selecione a visualização", ["Dashboard", "Tabela"])

# Estilos CSS
st.markdown("""
<style>
.event-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin: 20px 0 30px 0;
}
.fight-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
}
.card {
    background-color: #eeeeee;
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 0px 20px 10px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    width: 100%;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.corner-bar-blue {
    background-color: #007bff;
    height: 6px;
    width: 100%;
    border-radius: 10px 10px 0 0;
    margin-bottom: 6px;
}
.corner-bar-red {
    background-color: #dc3545;
    height: 6px;
    width: 100%;
    border-radius: 10px 10px 0 0;
    margin-bottom: 6px;
}
.card img {
    border-radius: 8px;
}
.info-block {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.status-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
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
    font-size: 22px;
    font-weight: 700;
    color: black;
    margin-bottom: 4px;
    text-align: center;
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
    font-size: 38px;
    font-weight: 800;
    color: #aaa;
    text-align: center;
    min-width: 140px;
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

def render_card(row, corner):
    bar_class = "corner-bar-blue" if corner == "BLUE" else "corner-bar-red"
    foto = f"<img src='{row['PHOTO1']}' width='80'>"
    nome = f"<div class='athlete-name'>{row.get('NAME', '')}</div>"
    status_html = "".join([
        status_tag(row.get('BLACK SCREEN', ''), "BLACK SCREEN"),
        status_tag(row.get('INTERVIEW', ''), "INTERVIEW"),
        status_tag(row.get('BLOOD TEST', ''), "BLOOD TEST"),
        status_tag(row.get('STATS', ''), "STATS"),
        status_tag(row.get('UNIFORM SIZE', ''), "UNIFORM SIZE"),
        status_tag(row.get('MUSIC', ''), "MUSIC")
    ])
    chegada = row.get("ARRIVAL", "")
    return f"""
    <div class='card'>
        <div class='{bar_class}'></div>
        {foto}
        <div class='info-block'>
            {nome}
            <div class='status-row'>{status_html}</div>
        </div>
        <div class='arrival-info'>{chegada}</div>
    </div>
    """

if pagina == "Dashboard":
    st.markdown(f"<div class='event-title'>UAEW Fightweek Tasks</div>", unsafe_allow_html=True)
    if {"PHOTO1", "CORNER", "FIGHT N", "EVENT"}.issubset(df.columns):
        df = df[df["PHOTO1"].astype(str).str.startswith("http", na=False)].copy()
        df.fillna("", inplace=True)
        df["FIGHT N"] = df["FIGHT N"].astype(str).str.zfill(2)
        df = df.sort_values(by=["EVENT", "FIGHT N", "CORNER"])

        for evento, grupo_evento in df.groupby("EVENT"):
            st.markdown(f"<div class='event-title'>{evento}</div>", unsafe_allow_html=True)
            for luta, luta_df in grupo_evento.groupby("FIGHT N"):
                blue = luta_df[luta_df["CORNER"].str.upper() == "BLUE"]
                red = luta_df[luta_df["CORNER"].str.upper() == "RED"]

                st.markdown("<div class='fight-line'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([5, 2, 5])

                with col1:
                    st.markdown(render_card(blue.iloc[0], "BLUE") if not blue.empty else "🟦 Sem atleta no corner BLUE", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='fight-number'>{luta}</div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(render_card(red.iloc[0], "RED") if not red.empty else "🔴 Sem atleta no corner RED", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("❌ Faltam colunas obrigatórias: 'PHOTO1', 'CORNER', 'FIGHT N', 'EVENT'")

elif pagina == "Tabela":
    st.title("Tabela de Acompanhamento Completa")
    st.dataframe(df)
