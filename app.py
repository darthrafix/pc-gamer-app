import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🎮 Monte seu PC Gamer")
st.caption("Compare builds e encontre os melhores preços")

SERP_API_KEY = st.secrets.get("SERPAPI_KEY")

# ---------------- BUSCA ----------------
def buscar_produtos(produto):
    if not SERP_API_KEY:
        return []

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

        resultados = []

        for item in data.get("shopping_results", [])[:6]:
            preco = item.get("price")

            if not preco:
                continue

            try:
                preco = float(
                    preco.replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
            except:
                continue

            resultados.append({
                "titulo": item.get("title", "Produto"),
                "preco": int(preco),
                "link": item.get("link", "#"),
                "fonte": item.get("source", "Loja")
            })

        return sorted(resultados, key=lambda x: x["preco"])

    except:
        return []


# ---------------- FALLBACK ----------------
preco_base = {
    "Ryzen 5 5600": 800,
    "Ryzen 7 5700X": 1200,
    "RTX 4060 8GB": 2200,
    "RTX 4070": 3800,
    "RX 6600": 1400,
    "B550M": 700,
    "16GB DDR4": 400,
    "32GB DDR4": 800,
    "Fonte 500W": 300,
    "Fonte 600W": 400,
    "Fonte 650W": 500
}

def fallback_preco(produto):
    for key in preco_base:
        if key in produto:
            return preco_base[key]
    return 0


# ---------------- BUILDS ----------------
builds = {
    "🟢 Básico": {
        "CPU": "Ryzen 5 5600",
        "GPU": "RX 6600",
        "RAM": "16GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 500W"
    },
    "🟡 Intermediário": {
        "CPU": "Ryzen 5 5600",
        "GPU": "RTX 4060 8GB",
        "RAM": "16GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 600W"
    },
    "🔴 Top": {
        "CPU": "Ryzen 7 5700X",
        "GPU": "RTX 4070",
        "RAM": "32GB DDR4",
        "Placa-mãe": "B550M",
        "Fonte": "Fonte 650W"
    }
}


# ---------------- UI ----------------
if st.button("🚀 Analisar builds"):

    cols = st.columns(3)

    for col, (nome_build, componentes) in zip(cols, builds.items()):
        with col:

            st.subheader(nome_build)

            total = 0

            for tipo, produto in componentes.items():

                resultados = buscar_produtos(produto)

                # 🔥 fallback se API falhar
                if not resultados:
                    preco = fallback_preco(produto)

                    st.markdown(f"""
                    <div style="background:#fff3cd;padding:12px;border-radius:10px;margin-bottom:10px;">
                        <b>{tipo}</b><br>
                        {produto}<br>
                        💰 R$ {preco} (estimado)
                    </div>
                    """, unsafe_allow_html=True)

                    total += preco
                    continue

                melhor = resultados[0]
                total += melhor["preco"]

                lojas_html = ""

                for i, r in enumerate(resultados):
                    destaque = "background:#ecfdf5;" if i == 0 else ""

                    lojas_html += f"""
                    <div style="display:flex;justify-content:space-between;padding:8px;{destaque}">
                        <div>{r["fonte"]}</div>
                        <div>
                            R$ {r["preco"]}
                            <a href="{r["link"]}" target="_blank">🔗</a>
                        </div>
                    </div>
                    """

                card_html = f"""
                <div style="background:white;border:1px solid #ddd;border-radius:12px;margin-bottom:10px;">
                    <div style="padding:10px;background:#f5f5f5;">
                        <b>{tipo}</b><br>
                        {produto}
                    </div>

                    <div style="padding:10px;">
                        💰 Melhor: R$ {melhor["preco"]}
                    </div>

                    {lojas_html}
                </div>
                """

                st.markdown(card_html, unsafe_allow_html=True)

            st.success(f"💸 Total: R$ {total}")
