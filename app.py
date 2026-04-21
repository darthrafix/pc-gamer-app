import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🎮 Monte seu PC Gamer")
st.caption("Os melhores preços, peça por peça, atualizados em tempo real.")

# 🔐 API
SERP_API_KEY = st.secrets.get("SERPAPI_KEY")

if not SERP_API_KEY:
    st.error("API key da SerpAPI não encontrada.")
    st.stop()

# ---------------- BUSCA ----------------
def buscar_produtos(produto):
    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google_shopping",
        "q": produto,
        "api_key": SERP_API_KEY,
        "hl": "pt",
        "gl": "br"
    }

    try:
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

        resultados = sorted(resultados, key=lambda x: x["preco"])
        return resultados

    except Exception as e:
        return []

# ---------------- BUILD ----------------
build = {
    "CPU": "Ryzen 5 5600 AM4",
    "GPU": "RTX 4060 8GB Gigabyte",
    "RAM": "16GB DDR4 3200MHz",
    "Placa-mãe": "B550M AM4",
    "Fonte": "Fonte 600W 80 Plus"
}

# ---------------- UI ----------------
if st.button("🚀 Buscar melhores preços"):

    total = 0

    for tipo, produto in build.items():

        resultados = buscar_produtos(produto)

        if not resultados:
            st.warning(f"{tipo}: sem resultados")
            continue

        melhor = resultados[0]
        total += melhor["preco"]

        # 🔥 monta lista de lojas
        lojas_html = ""

        for i, r in enumerate(resultados):

            destaque = "background:#ecfdf5;" if i == 0 else ""
            botao = "Comprar" if i == 0 else "Ver loja"
            cor_botao = "#4f46e5" if i == 0 else "#e5e7eb"
            cor_texto = "white" if i == 0 else "#374151"

            lojas_html += f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:12px 16px;
                border-top:1px solid #e5e7eb;
                {destaque}
            ">
                <div style="font-weight:600;">
                    {r["fonte"]}
                </div>

                <div style="display:flex; align-items:center; gap:16px;">
                    <div style="font-weight:700;">
                        R$ {r["preco"]}
                    </div>

                    <a href="{r["link"]}" target="_blank"
                        style="
                            background:{cor_botao};
                            color:{cor_texto};
                            padding:6px 12px;
                            border-radius:8px;
                            text-decoration:none;
                            font-weight:600;
                            font-size:14px;
                        ">
                        {botao}
                    </a>
                </div>
            </div>
            """

        # 🔥 card completo (CORRETO)
        card_html = f"""
        <div style="
            background:#ffffff;
            border-radius:16px;
            border:1px solid #e5e7eb;
            margin-top:20px;
            overflow:hidden;
        ">

            <div style="
                background:#f8fafc;
                padding:16px 20px;
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">
                <div>
                    <div style="font-size:11px; color:#94a3b8; font-weight:700;">
                        {tipo}
                    </div>
                    <div style="font-size:18px; font-weight:700;">
                        {produto}
                    </div>
                </div>

                <div style="
                    background:#d1fae5;
                    padding:8px 12px;
                    border-radius:999px;
                    font-weight:700;
                    color:#065f46;
                    font-size:14px;
                ">
                    R$ {melhor["preco"]}
                </div>
            </div>

            {lojas_html}

        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

    st.success(f"💸 Total estimado: R$ {total}")
