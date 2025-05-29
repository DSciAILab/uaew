import streamlit as st
import pandas as pd
import requests
import json
from streamlit_autorefresh import st_autorefresh
import base64

# Configuração da página
st.set_page_config(page_title="UAEW Fightweek Tasks", layout="wide")

# Atualiza a página automaticamente a cada 10 segundos
st_autorefresh(interval=10000, key="auto_refresh")

# CSV do Google Sheets
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRih5bZ-W7jgTsXbjE7mWpOQe8JeV4dQbMVH4gv9qhhkOc4NdKf-wXdRp7xwUtzZb8FqniMUt3VlXu-/pub?gid=330897584&single=true&output=csv"
df = pd.read_csv(csv_url)

# Carrega dados de perfil
@st.cache_data(ttl=60)
def carregar_perfis():
    url = f"https://raw.githubusercontent.com/{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO']}/main/{st.secrets['GITHUB_FILEPATH']}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

def salvar_perfis_json(perfis):
    api_url = f"https://api.github.com/repos/{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO']}/contents/{st.secrets['GITHUB_FILEPATH']}"
    headers = {
        "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }
    get_response = requests.get(api_url, headers=headers)
    sha = get_response.json().get("sha")
    content = json.dumps(perfis, indent=4).encode("utf-8")
    b64_content = base64.b64encode(content).decode("utf-8")
    data = {
        "message": "Atualiza perfil de atleta via Streamlit",
        "content": b64_content,
        "sha": sha
    }
    return requests.put(api_url, headers=headers, json=data)

# Sidebar para seleção de modo
pagina = st.sidebar.radio("Visualização", ["Dashboard", "Tabela", "Perfil do Atleta"])

if pagina == "Dashboard":
    st.title("UAEW Fightweek Tasks")

    st.markdown("""
    <style>
    .card {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 10px;
        position: relative;
    }
    .blue-bar {
        height: 8px;
        background-color: #007bff;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    .red-bar {
        height: 8px;
        background-color: #dc3545;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }
    .athlete-name {
        font-size: 22px;
        font-weight: 700;
        color: black;
        margin: 8px 0;
    }
    .fight-number {
        font-size: 42px;
        font-weight: bold;
        color: #666;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    if {"PHOTO1", "CORNER", "FIGHT N", "EVENT"}.issubset(df.columns):
        df = df[df["PHOTO1"].astype(str).str.startswith("http", na=False)].copy()
        df.fillna("", inplace=True)
        df["FIGHT N"] = df["FIGHT N"].astype(str).str.zfill(2)
        df = df.sort_values(by=["EVENT", "FIGHT N", "CORNER"])

        for evento, grupo_evento in df.groupby("EVENT"):
            st.subheader(evento)
            for luta, luta_df in grupo_evento.groupby("FIGHT N"):
                col1, col2, col3 = st.columns([5, 2, 5])

                with col1:
                    atleta_blue = luta_df[luta_df["CORNER"].str.upper() == "BLUE"]
                    if not atleta_blue.empty:
                        nome = atleta_blue.iloc[0]['NAME']
                        st.markdown("<div class='card'><div class='blue-bar'></div>", unsafe_allow_html=True)
                        st.image(atleta_blue.iloc[0]['PHOTO1'], width=80)
                        st.markdown(f"<div class='athlete-name'><a href='?athlete={nome}'>{nome}</a></div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown(f"<div class='fight-number'>{luta}</div>", unsafe_allow_html=True)

                with col3:
                    atleta_red = luta_df[luta_df["CORNER"].str.upper() == "RED"]
                    if not atleta_red.empty:
                        nome = atleta_red.iloc[0]['NAME']
                        st.markdown("<div class='card'><div class='red-bar'></div>", unsafe_allow_html=True)
                        st.image(atleta_red.iloc[0]['PHOTO1'], width=80)
                        st.markdown(f"<div class='athlete-name'><a href='?athlete={nome}'>{nome}</a></div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

elif pagina == "Tabela":
    st.title("Tabela de Acompanhamento Completa")
    st.dataframe(df)

elif pagina == "Perfil do Atleta":
    perfis = carregar_perfis()
    nomes_disponiveis = list(perfis.keys())

    if not nomes_disponiveis:
        st.warning("Nenhum atleta encontrado no arquivo de perfis.")
    else:
        atleta = st.selectbox("Selecione o atleta", nomes_disponiveis, index=0)

        dados = perfis.get(atleta, {"music": "", "height": "", "notes": ""})

        st.header(f"Perfil: {atleta}")
        music = st.text_input("Música", value=dados.get("music", ""))
        height = st.text_input("Altura", value=dados.get("height", ""))
        notes = st.text_area("Notas", value=dados.get("notes", ""))

        if st.button("Salvar alterações"):
            perfis[atleta] = {"music": music, "height": height, "notes": notes}
            salvar = salvar_perfis_json(perfis)
            if salvar.status_code == 200:
                st.success("Alterações salvas com sucesso!")
            else:
                st.error("Erro ao salvar no GitHub")
