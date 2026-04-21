import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🎮 PC Builder Inteligente (PRO)")

SERP_API_KEY = st.secrets["SERPAPI_KEY"]

# ---------------- SERP API ----------------
def buscar_serpapi(produto):
    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google_shopping",
        "q": produto,
        "api_key": SERP_API_KEY,
        "hl": "pt",
        "gl": "br"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        resultados = []

        for item in data.get("shopping_results", [])[:10]:
            preco = item.get("price")

            if preco:
                try:
                    preco = float(preco.replace("R$", "").replace(".", "").replace(",", "."))
                except:
                    continue

                resultados.append({
                    "titulo": item.get("title"),
                    "preco": int(preco),
                    "link": item.get("link"),
                    "fonte": item.get("source")
                })

        return resultados

    except:
        return []


# ---------------- INTELIGÊNCIA ----------------
def analisar_precos(resultados):
    if not resultados:
        return None, []

    precos = [r["preco"] for r in resultados]
    media = sum(precos) / len(precos)

    for r in resultados:
        r["score"] = (media - r["preco"]) / media

        if r["preco"] < media * 0.85:
            r["tag"] = "🔥 Promoção"
        elif r["preco"] < media:
            r["tag"] = "💰 Bom preço"
        else:
            r["tag"] = "😐 Normal"

    resultados = sorted(resultados, key=lambda x: x["preco"])

    return resultados[0], resultados


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
    "Starter": {
        "CPU": "Ryzen 5 5600G",
        "Placa-mãe": "B550M",
        "RAM": "16GB DDR4",
        "Fonte": "Fonte 500W"
    },
    "Intermediário": {
        "CPU": "Ryzen 5 5600",
        "GPU": "RX 6600",
        "Placa-mãe": "B550M",
        "RAM": "16GB DDR4",
        "Fonte": "Fonte 600W"
    },
    "Top": {
        "CPU": "Ryzen 7 5700X",
        "GPU": "RTX 4070",
        "Placa-mãe": "B550M",
        "RAM": "32GB DDR4",
        "Fonte": "Fonte 650W"
    }
}


# ---------------- UI ----------------
if st.button("🚀 Analisar builds (PRO)"):

    cols = st.columns(3)
    ranking = []

    for col, (nome, componentes) in zip(cols, builds.items()):
        with col:
            st.subheader(nome)
            total = 0

            for tipo, item in componentes.items():
                st.markdown(f"### {tipo}")

                if tipo in ["CPU", "GPU"]:
                    resultados = buscar_serpapi(item)
                    melhor, lista = analisar_precos(resultados)

                    if melhor:
                        total += melhor["preco"]

                        st.success(f"💰 R$ {melhor['preco']} — {melhor['tag']}")
                        st.caption(f"{melhor['fonte']}")

                        with st.expander("🛒 Ver opções"):
                            for r in lista:
                                st.markdown(
                                    f"[{r['titulo']} - R$ {r['preco']} ({r['tag']})]({r['link']})"
                                )
                    else:
                        st.warning("Sem resultados")

                else:
                    preco = preco_base.get(item, 0)
                    total += preco
                    st.info(f"💰 R$ {preco}")

                st.markdown("---")

            st.success(f"💸 Total: R$ {total}")

            ranking.append({"nome": nome, "preco": total})

    st.header("🏆 Melhor build")

    if ranking:
        best = min(ranking, key=lambda x: x["preco"])
        st.success(f"{best['nome']} → R$ {best['preco']}")
