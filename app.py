import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🎮 Monte seu PC Gamer")
st.caption("Os melhores preços, peça por peça, atualizados em tempo real.")

SERP_API_KEY = st.secrets["SERPAPI_KEY"]

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
        response = requests.get(url, params=params)
        data = response.json()

        resultados = []

        for item in data.get("shopping_results", [])[:6]:
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

        resultados = sorted(resultados, key=lambda x: x["preco"])
        return resultados

    except:
        return []


# ---------------- BUILDS ----------------
build = {
    "CPU": "Ryzen 5 5600",
    "GPU": "RTX 4060 8GB",
    "RAM": "16GB DDR4",
    "Placa-mãe": "B550M",
    "Fonte": "Fonte 600W"
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

        # -------- HEADER DO CARD --------
        st.markdown(f"""
        <div style="
            background:#f8fafc;
            padding:20px;
            border-radius:14px;
            border:1px solid #e5e7eb;
            margin-top:20px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:12px; color:#94a3b8; font-weight:700;">
                        {tipo}
                    </div>
                    <div style="font-size:20px; font-weight:700;">
                        {produto}
                    </div>
                </div>
                <div style="
                    background:#d1fae5;
                    padding:10px 14px;
                    border-radius:999px;
                    font-weight:700;
                    color:#065f46;
                ">
                    Melhor preço: R$ {melhor["preco"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # -------- LISTA DE LOJAS --------
        for i, r in enumerate(resultados):

            destaque = "background:#ecfdf5;" if i == 0 else ""
            botao = "Comprar" if i == 0 else "Ver loja"
            cor_botao = "#4f46e5" if i == 0 else "#e5e7eb"
            cor_texto = "white" if i == 0 else "#374151"

            st.markdown(f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:14px;
                border-top:1px solid #e5e7eb;
                {destaque}
            ">
                <div>
                    <div style="font-weight:600;">{r["fonte"]}</div>
                </div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-weight:700;">
                        R$ {r["preco"]}
                    </div>
                    <a href="{r["link"]}" target="_blank"
                        style="
                            background:{cor_botao};
                            color:{cor_texto};
                            padding:8px 14px;
                            border-radius:8px;
                            text-decoration:none;
                            font-weight:600;
                        ">
                        {botao}
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.success(f"💸 Total estimado: R$ {total}")
