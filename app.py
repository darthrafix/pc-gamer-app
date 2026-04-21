import streamlit as st
import requests
import json
import time
from statistics import mean

st.set_page_config(layout="wide")

# -------- STYLE (UI MELHORADA) --------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 16px;
    background: #111;
    border: 1px solid #222;
    margin-bottom: 15px;
}
.price {
    font-size: 22px;
    font-weight: bold;
}
.good { color: #00ff9f; }
.warn { color: #ffd166; }
.neutral { color: #999; }
.title {
    font-size: 28px;
    font-weight: 700;
}
.link-btn {
    display: inline-block;
    margin-right: 8px;
    margin-top: 6px;
    padding: 6px 10px;
    border-radius: 8px;
    background: #222;
    border: 1px solid #333;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎮 PC Builder Inteligente</div>', unsafe_allow_html=True)

# ---------------- PREÇO ----------------
def buscar_preco(produto):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
        data = requests.get(url).json()

        precos = [
            item["price"]
            for item in data.get("results", [])[:5]
            if item.get("price") and item["price"] > 100
        ]

        return int(sum(precos)/len(precos)) if precos else None
    except:
        return None


# ---------------- LINKS (COM SHOPEE) ----------------
def gerar_links(produto):
    termo = produto.replace(" ", "%20")

    return {
        "Kabum": f"https://www.kabum.com.br/busca/{produto}",
        "Amazon": f"https://www.amazon.com.br/s?k={produto}",
        "Pichau": f"https://www.pichau.com.br/search?q={produto}",
        "Terabyte": f"https://www.terabyteshop.com.br/busca?str={produto}",
        "Mercado Livre": f"https://lista.mercadolivre.com.br/{produto}",
        "Shopee": f"https://shopee.com.br/search?keyword={termo}"
    }


# ---------------- BASE ----------------
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
if st.button("🚀 Analisar builds"):

    cols = st.columns(3)
    ranking = []

    for col, (nome, itens) in zip(cols, builds.items()):
        with col:
            total = 0

            st.markdown(f"### {nome}")

            for item in itens:

                # preço dinâmico vs base
                if any(x in item for x in ["RTX", "RX", "Ryzen"]):
                    preco = buscar_preco(item)
                else:
                    preco = preco_base.get(item)

                if not preco:
                    preco_txt = "N/A"
                    color = "neutral"
                else:
                    preco_txt = f"R$ {preco}"
                    total += preco
                    color = "good"

                # CARD
                st.markdown(f"""
                <div class="card">
                    <b>{item}</b><br>
                    <span class="price {color}">{preco_txt}</span>
                </div>
                """, unsafe_allow_html=True)

                # LINKS DE COMPRA
                links = gerar_links(item)

                with st.expander("🛒 Ver opções de compra"):
                    for loja, url in links.items():
                        if loja == "Shopee":
                            st.markdown(f"[{loja}]({url}) ⚠️ verifique vendedor")
                        else:
                            st.markdown(f"[{loja}]({url})")

            # TOTAL
            st.markdown(f"""
            <div class="card">
                <b>Total</b><br>
                <span class="price good">R$ {total}</span>
            </div>
            """, unsafe_allow_html=True)

            ranking.append({"nome": nome, "preco": total})

    # MELHOR BUILD
    st.markdown("## 🏆 Melhor custo-benefício")

    ranking = [r for r in ranking if r["preco"] > 0]

    if ranking:
        best = min(ranking, key=lambda x: x["preco"])
        st.success(f"{best['nome']} → R$ {best['preco']}")
