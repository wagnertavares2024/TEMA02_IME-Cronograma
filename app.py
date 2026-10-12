"""Painel de controle TEMA02_IME — versão Streamlit.

Le o checklist mais recente em data/ (padrao *_checklist_tema02_R*.json,
pega o de maior revisao) e reproduz o mesmo painel do Artifact da claude.ai,
para compartilhamento fora do ecossistema Claude.
"""

import glob
import json
import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="TEMA02_IME", page_icon="📊", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

STATUS_COLOR = {
    "Cumprido": "#1f8a53",
    "Parcial": "#b9770e",
    "Não cumprido": "#c23b3b",
}
STATUS_BG = {
    "Cumprido": "#e5f5ec",
    "Parcial": "#fbf0dd",
    "Não cumprido": "#fbe8e8",
}


def carregar_checklist() -> dict:
    """Pega o JSON de maior revisão em data/ (ordenação lexicográfica cobre R00, R01...)."""
    candidatos = sorted(glob.glob(os.path.join(DATA_DIR, "*_checklist_tema02_R*.json")))
    if not candidatos:
        st.error(f"Nenhum arquivo de checklist encontrado em {DATA_DIR}")
        st.stop()
    with open(candidatos[-1], encoding="utf-8") as f:
        return json.load(f), os.path.basename(candidatos[-1])


def colorir_situacao(val: str) -> str:
    cor = STATUS_COLOR.get(val, "#1b2430")
    fundo = STATUS_BG.get(val, "#f4f6f9")
    return f"color: {cor}; background-color: {fundo}; font-weight: 600; border-radius: 6px; text-align: center;"


dados, arquivo_fonte = carregar_checklist()

st.caption(f"ET-260100 · IME — Engenharia de Transportes · fonte: `{arquivo_fonte}`")
st.title(f"{dados['titulo']} –")
st.write(
    f"Painel de controle das exigências rastreadas, lido de **{dados['fonte']}**. "
    f"Atualizado em {dados['atualizado_em']}."
)

todos_itens = [item for secao in dados["secoes"] for item in secao["itens"]]
total = len(todos_itens)
avanco_medio = sum(i["avanco"] for i in todos_itens) / total
n_cumprido = sum(1 for i in todos_itens if i["situacao"] == "Cumprido")
n_parcial = sum(1 for i in todos_itens if i["situacao"] == "Parcial")
n_nao = sum(1 for i in todos_itens if i["situacao"] == "Não cumprido")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avanço geral", f"{avanco_medio:.0f}%")
col2.metric("Cumprido", n_cumprido)
col3.metric("Parcial", n_parcial)
col4.metric("Não cumprido", n_nao)
st.progress(avanco_medio / 100)

st.divider()

for secao in dados["secoes"]:
    st.subheader(secao["nome"])
    df = pd.DataFrame(secao["itens"])
    df = df.rename(
        columns={
            "indice": "Índice",
            "origem": "Origem",
            "exigencia": "Exigência",
            "situacao": "Situação",
            "onde_esta": "Onde está / o que falta",
            "avanco": "Avanço (%)",
        }
    )
    styled = df.style.map(colorir_situacao, subset=["Situação"]).format({"Avanço (%)": "{:.0f}%"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "Critério de avanço: Cumprido = 100%, Não cumprido = 0%, Parcial = percentual estimado "
    "conforme a fração do escopo já atendida. Dado mantido manualmente em paralelo ao painel "
    "publicado como Claude Artifact — não é lido ao vivo do documento de etapas."
)
