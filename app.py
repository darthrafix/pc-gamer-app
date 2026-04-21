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
                    except:
                        pass
        except:
            pass

    # 🔹 FALLBACK (Mercado Livre)
    if not resultados:
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
            response = requests.get(url, timeout=10)
            data = response.json()

            for item in data.get("results", [])[:5]:
                preco = item.get("price")

                if preco:
                    resultados.append({
                        "preco": int(preco),
                        "link": item.get("permalink", "#"),
                        "fonte": "Mercado Livre"
                    })
        except:
            pass

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

                # 🔥 GARANTE QUE SEMPRE TEM DADO
                if not resultados:
                    resultados = [{
                        "preco": 0,
                        "link": "#",
                        "fonte": "Sem dados"
                    }]

                melhor = resultados[0]
                total += melhor["preco"]

                # 🔥 lista de lojas
                lojas_html = ""

                for r in resultados:
                    lojas_html += f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        padding:6px 0;
                        border-bottom:1px solid #eee;
                        font-size:13px;
                    ">
                        <span>{r["fonte"]}</span>
                        <span>
                            R$ {r["preco"]}
                            <a href="{r["link"]}" target="_blank">🔗</a>
                        </span>
                    </div>
                    """

                # 🔥 CARD LIMPO (CLARO, IGUAL COMPARADOR)
                card_html = f"""
                <div style="
                    background:white;
                    border-radius:14px;
                    padding:16px;
                    margin-bottom:12px;
                    border:1px solid #ddd;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);
                ">

                    <div style="font-size:12px;color:#888;">
                        {tipo.upper()}
                    </div>

                    <div style="font-size:18px;font-weight:700;">
                        {produto}
                    </div>

                    <div style="
                        margin-top:10px;
                        background:#e6f4ea;
                        color:#137333;
                        padding:8px;
                        border-radius:8px;
                        font-weight:600;
                        font-size:13px;
                    ">
                        💰 Melhor preço: R$ {melhor["preco"]} ({melhor["fonte"]})
                    </div>

                    <div style="margin-top:10px;">
                        {lojas_html}
                    </div>

                </div>
                """

                st.markdown(card_html, unsafe_allow_html=True)

            st.success(f"💸 Total: R$ {total}")
