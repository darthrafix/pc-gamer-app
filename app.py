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

            data = requests.get(url, params=params).json()

            for item in data.get("shopping_results", [])[:5]:
                preco = item.get("price")

                if preco:
                    try:
                        preco = float(preco.replace("R$", "").replace(".", "").replace(",", "."))
                        resultados.append({
                            "preco": int(preco),
                            "link": item.get("link"),
                            "fonte": item.get("source")
                        })
                    except:
                        pass
        except:
            pass

    # 🔹 FALLBACK ML
    if not resultados:
        try:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={produto}"
            data = requests.get(url).json()

            for item in data.get("results", [])[:5]:
                preco = item.get("price")

                if preco:
                    resultados.append({
                        "preco": int(preco),
                        "link": item.get("permalink"),
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

                if not resultados:
                    continue

                melhor = resultados[0]
                total += melhor["preco"]

                # 🔥 lista lojas
                lojas_html = ""

                for r in resultados:
                    lojas_html += f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        padding:6px 0;
                        color:#d1d5db;
                    ">
                        <span>{r["fonte"]}</span>
                        <span>R$ {r["preco"]}</span>
                    </div>
                    """

                # 🔥 CARD PADRÃO (igual seu exemplo)
                st.markdown(f"""
                <div style="
                    background:linear-gradient(135deg,#1f2937,#111827);
                    border-radius:16px;
                    padding:16px;
                    margin-bottom:12px;
                    border:1px solid #374151;
                ">

                    <div style="color:#9ca3af;font-size:12px;">
                        {tipo.upper()}
                    </div>

                    <div style="color:white;font-size:18px;font-weight:700;">
                        {produto}
                    </div>

                    <div style="
                        margin-top:10px;
                        background:#065f46;
                        color:#6ee7b7;
                        padding:8px;
                        border-radius:10px;
                        font-weight:600;
                        font-size:13px;
                    ">
                        💰 Melhor preço: R$ {melhor["preco"]} ({melhor["fonte"]})
                    </div>

                    <div style="margin-top:10px;">
                        {lojas_html}
                    </div>

                </div>
                """, unsafe_allow_html=True)

            st.success(f"💸 Total: R$ {total}")
