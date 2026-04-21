import streamlit as st
import requests
import json
import time
from statistics import mean

st.set_page_config(layout="wide")

st.title("🎮 PC Gamer Builder Inteligente (v2)")
st.markdown("Comparação com preço real, score e ranking de custo-benefício.")

# ---------------- PREÇO REAL (ML + fallback) ----------------
def buscar_preco_ml(produto):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
        r = requests.get(url)
        data = r.json()

        resultados = data.get("results", [])[:5]

        precos = []
        for item in resultados:
            p = item.get("price")
            if p and p > 100:
                precos.append(p)

        if precos:
            return int(sum(precos) / len(precos))

        return None
    except:
        return None


def buscar_preco(produto):
    preco = buscar_preco_ml(produto)

    if preco:
        return preco

    return None


# ---------------- HISTÓRICO ROBUSTO ----------------
def salvar_historico(produto, preco):
    try:
        with open("historico.json", "r") as f:
            hist = json.load(f)
    except:
        hist = {}

    serie = hist.get(produto, [])

    if not isinstance(serie, list):
        serie = []

    serie.append({"t": int(time.time()), "p": preco})

    hist[produto] = serie[-20:]

    with open("historico.json", "w") as f:
        json.dump(hist, f)

    return hist[produto]


# ---------------- SCORE ----------------
def score_compra(serie):
    if len(serie) < 3:
        return "Neutro", 0

    precos = [p["p"] for p in serie]
    atual = precos[-1]
    media = mean(precos)

    score = (media - atual) / media

    if score > 0.08:
        return "Comprar", score
    elif score < -0.05:
        return "Esperar", score
    else:
        return "Ok", score


# ---------------- FPS ----------------
def fps_estimado(gpu, jogo):
    tabela = {
        "RX 6600": {"Cyberpunk": 50, "GTA": 75, "EA FC": 120},
        "RTX 4060": {"Cyberpunk": 75, "GTA": 100, "EA FC": 144},
        "RTX 4070": {"Cyberpunk": 110, "GTA": 130, "EA FC": 180}
    }

    for k in tabela:
        if k in gpu:
            return tabela[k].get(jogo, 60)

    return 40


# ---------------- LINKS ----------------
def gerar_links(produto):
    return {
        "Kabum": f"https://www.kabum.com.br/busca/{produto}",
        "Amazon": f"https://www.amazon.com.br/s?k={produto}",
        "Pichau": f"https://www.pichau.com.br/search?q={produto}",
        "Terabyte": f"https://www.terabyteshop.com.br/busca?str={produto}",
        "Mercado Livre": f"https://lista.mercadolivre.com.br/{produto}"
    }


# ---------------- PREÇOS BASE ----------------
preco_base = {
    "B550M": 800,
    "16GB DDR4": 650,
    "32GB DDR4": 1200,
    "Fonte 500W": 350,
    "Fonte 600W": 400,
    "Fonte 650W": 500
}


# ---------------- BUILDS ----------------
builds = {
    "Starter": [
        "Ryzen 5 5600G",
        "B550M",
        "16GB DDR4",
        "Fonte 500W"
    ],
    "Intermediário": [
        "Ryzen 5 5600",
        "RX 6600 ASRock",
        "B550M",
        "16GB DDR4",
        "Fonte 600W"
    ],
    "Top": [
        "Ryzen 7 5700X",
        "RTX 4070 Gigabyte",
        "B550M",
        "32GB DDR4",
        "Fonte 650W"
    ]
}


# ---------------- UI ----------------
if st.button("🔄 Atualizar preços"):

    cols = st.columns(3)
    ranking = []

    for col, (nome, itens) in zip(cols, builds.items()):
        with col:
            st.subheader(nome)

            total = 0
            score_total = 0

            for item in itens:

                if "RTX" in item or "RX" in item or "Ryzen" in item:
                    preco = buscar_preco(item)
                else:
                    preco = preco_base.get(item)

                if not preco:
                    preco = 0

                st.markdown(f"**{item}**")
                st.write(f"💰 R$ {preco}")

                if preco > 0:
                    serie = salvar_historico(item, preco)
                    decisao, score = score_compra(serie)

                    score_total += score

                    if decisao == "Comprar":
                        st.success("🟢 Comprar")
                    elif decisao == "Esperar":
                        st.warning("🟡 Esperar")
                    else:
                        st.info("🔵 Ok")

                    total += preco

                links = gerar_links(item)

                with st.expander("Comprar"):
                    for loja, url in links.items():
                        st.markdown(f"[{loja}]({url})")

                st.markdown("---")

            st.success(f"💸 Total: R$ {total}")

            jogo = st.selectbox(
                "FPS",
                ["Cyberpunk", "GTA", "EA FC"],
                key=nome
            )

            gpu = [i for i in itens if "RTX" in i or "RX" in i]
            gpu_nome = gpu[0] if gpu else "Integrada"

            fps = fps_estimado(gpu_nome, jogo)

            st.write(f"🎮 FPS: {fps}")

            ranking.append({
                "nome": nome,
                "preco": total,
                "score": score_total
            })

    # ---------------- RANKING ----------------
    st.header("🏆 Ranking de custo-benefício")

    ranking.sort(key=lambda x: (x["preco"], -x["score"]))

    for r in ranking:
        st.write(f"{r['nome']} → R$ {r['preco']}")
