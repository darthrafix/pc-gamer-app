import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🎮 PC Builder Inteligente (Zoom-like)")

# ---------------- BUSCA REAL ----------------
def buscar_produtos(produto):
    try:
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
        data = requests.get(url).json()

        resultados = []

        for item in data.get("results", [])[:5]:
            preco = item.get("price")

            if preco and preco > 100:
                resultados.append({
                    "titulo": item.get("title"),
                    "preco": preco,
                    "link": item.get("permalink")
                })

        return resultados

    except:
        return []


# ---------------- PREÇO BASE ----------------
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
    "Starter": {
        "CPU": "Ryzen 5 5600G",
        "Placa-mãe": "B550M",
        "RAM": "16GB DDR4",
        "Fonte": "Fonte 500W"
    },
    "Intermediário": {
        "CPU": "Ryzen 5 5600",
        "GPU": "RX 6600 ASRock",
        "Placa-mãe": "B550M",
        "RAM": "16GB DDR4",
        "Fonte": "Fonte 600W"
    },
    "Top": {
        "CPU": "Ryzen 7 5700X",
        "GPU": "RTX 4070 Gigabyte",
        "Placa-mãe": "B550M",
        "RAM": "32GB DDR4",
        "Fonte": "Fonte 650W"
    }
}


# ---------------- UI ----------------
if st.button("🔍 Buscar melhores preços"):

    cols = st.columns(3)
    ranking = []

    for col, (nome, componentes) in zip(cols, builds.items()):
        with col:
            st.subheader(nome)

            total = 0

            for tipo, item in componentes.items():

                st.markdown(f"### {tipo}")

                # 🔥 busca real ou base
                if tipo in ["CPU", "GPU"]:
                    resultados = buscar_produtos(item)

                    if resultados:
                        menor = min(r["preco"] for r in resultados)
                        total += menor

                        st.success(f"💰 A partir de R$ {menor}")

                        # opções
                        for r in resultados:
                            st.markdown(f"[🛒 {r['titulo']} - R$ {r['preco']}]({r['link']})")

                    else:
                        st.warning("⚠️ preço não encontrado")

                else:
                    preco = preco_base.get(item, 0)
                    total += preco

                    st.info(f"💰 R$ {preco}")

                    st.markdown(f"[🔎 Buscar {item}](https://www.google.com/search?q={item}+preço)")

                st.markdown("---")

            st.success(f"💸 Total estimado: R$ {total}")

            ranking.append({"nome": nome, "preco": total})

    # ---------------- RANKING ----------------
    st.header("🏆 Melhor build hoje")

    ranking = [r for r in ranking if r["preco"] > 0]

    if ranking:
        best = min(ranking, key=lambda x: x["preco"])
        st.success(f"{best['nome']} → R$ {best['preco']}")
