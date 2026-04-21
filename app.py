import streamlit as st
import random

st.set_page_config(layout="wide")

st.title("🎮 PC Gamer Finder (Live)")

st.markdown("Compare builds, preços e custo-benefício em tempo real.")

def gerar_dados():
    return [
        {"nome": "RTX 4070", "loja": "Kabum", "preco": random.randint(3800, 4500), "score": 9.5},
        {"nome": "RTX 4060", "loja": "Amazon", "preco": random.randint(2000, 2600), "score": 8.0},
        {"nome": "RX 6600", "loja": "Pichau", "preco": random.randint(1200, 1600), "score": 6.5}
    ]

if st.button("🔄 Atualizar preços"):
    dados = gerar_dados()

    st.subheader("📊 Comparação de GPUs")

    for item in dados:
        st.markdown(f"""
        ### {item['nome']}
        🏪 Loja: {item['loja']}  
        💰 Preço: R$ {item['preco']}  
        ⭐ Score: {item['score']}  
        ---
        """)

    melhor = max(dados, key=lambda x: x["score"])
    st.success(f"🏆 Melhor compra hoje: {melhor['nome']} por R$ {melhor['preco']}")

st.sidebar.header("🎯 Build alvo")
st.sidebar.markdown("""
- Plataforma: AM4  
- Objetivo: RTX 4070  
- Upgrade futuro: 32GB RAM  
""")
