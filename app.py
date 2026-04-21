import streamlit as st
import requests
import json
import time
from statistics import mean

st.set_page_config(layout="wide")

st.title("🎮 PC Gamer Builder Inteligente")
st.markdown("Compare builds completas com preços reais, histórico e recomendação de compra.")

# ---------------- PREÇO REAL ----------------
def buscar_preco(produto):
    try:
        termo = produto.replace(" ", "%20")
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo}"

        response = requests.get(url)
        data = response.json()

        resultados = data.get("results", [])[:5]

        precos = []

        for item in resultados:
            if item.get("price") and item.get("price") > 100:
                precos.append(item["price"])

        if precos:
            return int(sum(precos) / len(precos))

        return None

    except:
        return None


# ---------------- HISTÓRICO ----------------
def salvar_historico(produto, preco):
    try:
        with open("historico.json", "r") as f:
            hist = json.load(f)
    except:
        hist = {}

    serie = hist.get(produto, [])
    serie.append({"t": int(time.time()), "p": preco})

    hist[produto] = serie[-20:]

    with open("historico.json", "w") as f:
        json.dump(hist, f)

    return hist[produto]


def detectar_queda(serie):
    if len(serie) < 2:
        return False
    return serie[-1]["p"] < serie[-2]["p"]


# ---------------- SCORE ----------------
def score_compra(serie):
    if len(serie) < 3:
        return "Neutro", "Pouco histórico"

    precos = [p["p"] for p in serie]
    atual = precos[-1]
    media = mean(precos)

    delta = (media - atual) / media

    if delta > 0.08:
        return "Comprar", "Preço abaixo da média"
    elif delta < -0.05:
        return "Esperar", "Preço acima da média"
    else:
        return "Ok", "Dentro da média"


# ---------------- FPS ----------------
def fps_estimado(gpu, jogo):
    base = {
        "RX 6600": {"Cyberpunk": 50, "GTA": 75, "EA FC": 120},
        "RTX 4060": {"Cyberpunk": 75, "GTA": 100, "EA FC": 144},
        "RTX 4070": {"Cyberpunk": 110, "GTA": 130, "EA FC": 180},
    }

    for k in base:
        if k in gpu:
            return base[k].get(jogo, 60)

    return 40


# ---------------- LINKS ----------------
def gerar_links(produto):
    return {
        "Kabum": f"https://www.kabum.com.br/busca/{produto.replace(' ', '-')}",
        "Amazon": f"https://www.amazon.com.br/s?k={produto.replace(' ', '+')}",
        "Pichau": f"https://www.pichau.com.br/search?q={produto}",
        "Terabyte": f"https://www.terabyteshop.com.br/busca?str={produto}",
        "Mercado Livre": f"https://lista.mercadolivre.com.br/{produto.replace(' ', '-')}",
        "Shopee (⚠️)": f"https://shopee.com.br/search?keyword={produto}"
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
    "🟢 Starter (Jogável)": [
        "Ryzen 5 5600G",
        "B550M",
        "16GB DDR4",
        "Fonte 500W"
    ],
    "⚖️ Intermediário": [
        "Ryzen 5 5600",
        "RX 6600 ASRock Challenger",
        "B550M",
        "16GB DDR4",
        "Fonte 600W"
    ],
    "🔥 Top (Longo prazo)": [
        "Ryzen 7 5700X",
        "RTX 4070 Gigabyte Windforce OC",
        "B550M",
        "32GB DDR4",
        "Fonte 650W"
    ]
}


# ---------------- UI ----------------
if st.button("🔄 Atualizar preços"):

    cols = st.columns(3)
    comparacao = []

    for col, (nome, componentes) in zip(cols, builds.items()):
        with col:
            st.subheader(nome)

            total = 0

            for item in componentes:

                # 🔹 lógica híbrida
                if "RTX" in item or "RX" in item or "Ryzen" in item:
                    preco = buscar_preco(item)
                else:
                    preco = preco_base.get(item, 0)

                if not preco:
                    preco = "N/A"

                st.markdown(f"**{item}**")
                st.markdown(f"💰 R$ {preco}")

                # 📉 histórico + score
                if isinstance(preco, int):
                    serie = salvar_historico(item, preco)

                    if detectar_queda(serie):
                        st.success("🔥 Preço caiu!")

                    decisao, motivo = score_compra(serie)

                    if decisao == "Comprar":
                        st.success(f"🟢 {decisao}: {motivo}")
                    elif decisao == "Esperar":
                        st.warning(f"🟡 {decisao}: {motivo}")
                    else:
                        st.info(f"🔵 {decisao}: {motivo}")

                # 🛒 links
                links = gerar_links(item)

                with st.expander("🛒 Comprar"):
                    for loja, url in links.items():
                        st.markdown(f"[{loja}]({url})")

                st.markdown("---")

                # 💰 soma
                if isinstance(preco, int):
                    total += preco

            st.success(f"💸 Total: R$ {total}")

            # 🎮 FPS
            jogo = st.selectbox(
                "Simular FPS",
                ["Cyberpunk", "GTA", "EA FC"],
                key=f"fps_{nome}"
            )

            gpu_build = [c for c in componentes if "RTX" in c or "RX" in c]
            gpu_nome = gpu_build[0] if gpu_build else "Integrada"

            fps = fps_estimado(gpu_nome, jogo)

            st.markdown(f"🎮 FPS estimado ({jogo}): **{fps} FPS**")

            comparacao.append({
                "nome": nome,
                "preco": total
            })

    # ---------------- MELHOR BUILD ----------------
    st.header("📊 Melhor build hoje")

    if comparacao:
        melhor = min(comparacao, key=lambda x: x["preco"])
        st.success(f"🏆 Melhor custo hoje: {melhor['nome']} por R$ {melhor['preco']}")


# ---------------- SIDEBAR ----------------
st.sidebar.header("🎯 Estratégia de Upgrade")

st.sidebar.markdown("""
🟢 Comece com Starter  
⬇  
⚖️ Adicione GPU → Intermediário  
⬇  
🔥 Upgrade GPU + RAM → Top  
""")
