"""Gera o README.md a partir do JSON de maior revisão em data/."""

import glob
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
arquivo = sorted(glob.glob(os.path.join(AQUI, "data", "*_checklist_tema02_R*.json")))[-1]
with open(arquivo, encoding="utf-8") as f:
    d = json.load(f)

itens = [i for s in d["secoes"] for i in s["itens"]]
media = sum(i["avanco"] for i in itens) / len(itens)


def contar(situacao):
    return sum(1 for i in itens if i["situacao"] == situacao)


def esc(texto):
    return str(texto).replace("|", "\\|")


linhas = [
    f"# {d['titulo']} – Cronograma e controle de exigências",
    "",
    f"Painel de controle das exigências da proposta de dissertação (IME, Engenharia de Transportes). "
    f"Atualizado em {d['atualizado_em']}. Fonte: {d['fonte']}.",
    "",
    f"**Avanço geral: {media:.0f}%** — Cumprido: {contar('Cumprido')} · Parcial: {contar('Parcial')} · "
    f"Não cumprido: {contar('Não cumprido')} (total: {len(itens)} exigências).",
    "",
    "Critério: Cumprido = 100%, Não cumprido = 0%, Parcial = percentual estimado conforme a fração do escopo já atendida.",
    "",
]
for secao in d["secoes"]:
    linhas += [f"## {secao['nome']}", "",
               "| Índice | Origem | Exigência | Situação | Onde está / o que falta | Avanço |",
               "|---|---|---|---|---|---|"]
    for i in secao["itens"]:
        linhas.append(
            f"| {i['indice']} | {esc(i['origem'])} | {esc(i['exigencia'])} | {i['situacao']} | "
            f"{esc(i['onde_esta'])} | {i['avanco']}% |"
        )
    linhas.append("")
linhas += ["## Comentários do orientador", "", "Comentários por etapa ficam nas Issues deste repositório.", ""]

with open(os.path.join(AQUI, "README.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))
print(f"README gerado a partir de {os.path.basename(arquivo)}: {len(itens)} itens, avanço {media:.0f}%")
