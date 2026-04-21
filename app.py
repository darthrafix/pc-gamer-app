import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🖥️ Comparador de Peças PC Gamer")

SERP_API_KEY = st.secrets.get("SERPAPI_KEY")

# ---------------- BUSCA ----------------
def buscar_produtos(produto):
    resultados = []

    # 🔹 SERPAPI
    if SERP_API_KEY:
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_shopping",
                "q": produto,
                "api_key": SERP_API_KEY,
                "hl": "pt",
                "gl": "br"
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # DEBUG
            if "error" in data:
                st.warning(f"SerpAPI erro: {data['error']}")

            for item in data.get("shopping_results", [])[:5]:
                preco = item.get("price")

                if preco:
                    try:
                        preco = float(preco.replace("R$", "").replace(".", "").replace(",", "."))
                        resultados.append({
                            "preco": int(preco),
                            "link": item.get("link", "#"),
                            "fonte": item.get("source", "Loja")
                        })
                    except Exception as e:
                        st.warning(f"Erro parse preço: {e}")

        except Exception as e:
            st.error(f"Erro SerpAPI: {e}")

    # 🔹 MERCADO LIVRE (forçado)
    if not resultados:
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if "results" not in data:
                st.warning(f"ML resposta estranha: {data}")

            for item in data.get("results", [])[:5]:
                preco = item.get("price")

                if preco:
                    resultados.append({
                        "preco": int(preco),
                        "link": item.get("permalink", "#"),
                        "fonte": "Mercado Livre"
                    })

        except Exception as e:
            st.error(f"Erro Mercado Livre: {e}")

    return sorted(resultados, key=lambda x: x["preco"])


# ---------------- BUILDS ----------------
builds = {
    "🟢 Básico": {
        "Processador": "Ryzen 5 5600",
        "GPU": "RX 6600",
        "RAM": "16GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 500W"
    },
    "🟡 Intermediário": {
        "Processador": "Ryzen 5 5600",
        "GPU": "RTX 4060",
        "RAM": "16GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 600W"
    },
    "🔴 Top": {
        "Processador": "Ryzen 7 5700X",
        "GPU": "RTX 4070",
        "RAM": "32GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 650W"
    }
}


# ---------------- UI ----------------
if st.button("🚀 Buscar preços"):

    cols = st.columns(3)

    for col, (nome, componentes) in zip(cols, builds.items()):
        with col:
            st.subheader(nome)

            total = 0

            for tipo, produto in componentes.items():

                resultados = buscar_produtos(produto)

                if not resultados:
                    resultados = [{
                        "preco": 0,
                        "link": "#",
                        "fonte": "Sem dados"
                    }]

                melhor = resultados[0]
                total += melhor["preco"]

                lojas_html = ""

                for r in resultados:
                    lojas_html += f"""
                    <div style="display:flex;justify-content:space-between;padding:6px 0;">
                        <span>{r["fonte"]}</span>
                        <span>R$ {r["preco"]}</span>
                    </div>
                    """

                st.markdown(f"""
                <div style="background:white;padding:12px;border-radius:12px;margin-bottom:10px;">
                    <b>{tipo}</b><br>
                    {produto}<br><br>
                    💰 R$ {melhor["preco"]} ({melhor["fonte"]})
                    {lojas_html}
                </div>
                """, unsafe_allow_html=True)

            st.success(f"💸 Total: R$ {total}")
