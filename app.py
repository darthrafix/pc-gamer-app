import streamlit as st
import requests
import json

st.set_page_config(layout="wide")

st.title("🎮 PC Gamer Builder Inteligente")

st.markdown("Compare builds completas com preços reais e evolução de upgrade.")

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
def verificar_queda(produto, preco_atual):
    try:
        with open("historico.json", "r") as f:
            hist = json.load(f)
    except:
        hist = {}

    preco_antigo = hist.get(produto)
    hist[produto] = preco_atual

    with open("historico.json", "w") as f:
        json.dump(hist, f)

    return preco_antigo and preco_atual < preco_antigo


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
        "RX 6600",
        "B550M",
        "16GB DDR4",
        "Fonte 600W"
    ],
    "🔥 Top (Longo prazo)": [
        "Ryzen 5 5600 / 5700X",
        "RTX 4070",
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

                preco = buscar_preco(item)

                if not preco:
                    preco = "N/A"

                if isinstance(preco, int):
                total += preco

                st.markdown(f"**{item}**")
                st.markdown(f"💰 R$ {preco}")

                if preco > 0 and verificar_queda(item, preco):
                    st.success("🔥 Preço caiu!")

                links = gerar_links(item)

                with st.expander("🛒 Comprar"):
                    for loja, url in links.items():
                        st.markdown(f"[{loja}]({url})")

                st.markdown("---")

            st.success(f"💸 Total: R$ {total}")

            comparacao.append({"nome": nome, "preco": total})

# ---------------- COMPARAÇÃO ----------------

    st.header("📊 Melhor build hoje")

    melhor = min(comparacao, key=lambda x: x["preco"])

    st.success(f"🏆 Melhor custo hoje: {melhor['nome']} por R$ {melhor['preco']}")

# ---------------- SIDEBAR ----------------

st.sidebar.header("🎯 Estratégia")

st.sidebar.markdown("""
Comece com Starter  
⬇  
Adicione GPU → Intermediário  
⬇  
Upgrade GPU + RAM → Top  
""")
