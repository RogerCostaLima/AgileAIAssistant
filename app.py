# app.py
import streamlit as st
import json
import time
from ia_models import gerar_resposta_gemini, gerar_resposta_gpt, gerar_resposta_copilot
from utils import exportar_artefatos, baixar_excel, extrair_texto_ppt
import pandas as pd
import requests
#from streamlit_lottie import st_lottie


# =====================
# CONFIGURAÇÃO DE PÁGINA
# =====================
st.set_page_config(page_title="Assistente Ágil IA", layout="wide", page_icon="🤖")

CONFIG_FILE = "config.json"
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    st.error("Arquivo config.json não encontrado. Crie um antes de rodar o app.")
    st.stop()

# =====================
# FUNÇÃO PARA LOTTIE
# =====================
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# =====================
# MENU LATERAL
# =====================
st.sidebar.title("🤖 Assistente Ágil")
menu_option = st.sidebar.radio(
    "Menu",
    ["🧠 Geração de Artefatos", "⚙️ Configurações de IA", "📂 Exportação", "ℹ️ Sobre"]
)

# =====================
# CONFIGURAÇÕES DE IA
# =====================
if menu_option == "⚙️ Configurações de IA":
    st.header("Configurações Avançadas da IA")

    # Chaves de API
    st.subheader("API Keys")
    for key in config["api_keys"]:
        config["api_keys"][key] = st.text_input(
            f"{key.upper()} API Key",
            value=config["api_keys"][key],
            type="password"
        )

    # Papel da IA
    st.subheader("Como a IA deve atuar")
    config["ia_role"] = st.text_area(
        "Descreva como a IA deve atuar (ex: Especialista em Metodologia Ágil, seguindo práticas do playbook fornecido)",
        value=config.get("ia_role", ""),
        height=80
    )

    # Upload do PPT (Playbook ágil)
    arquivo_ppt = st.file_uploader("📄 Upload de Playbook em PPT (opcional)", type=["pptx"])
    if arquivo_ppt:
        config["playbook_text"] = extrair_texto_ppt(arquivo_ppt)
        st.success("Playbook carregado e processado com sucesso!")

    # Prompts padrão
    st.subheader("Prompts Padrão por Artefato")
    for p in config["prompts"]:
        config["prompts"][p] = st.text_area(
            f"Prompt para {p.upper()}",
            value=config["prompts"][p],
            height=100
        )

    if st.button("💾 Salvar Configurações"):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        st.success("✅ Configurações salvas com sucesso!")

# =====================
# SOBRE
# =====================
elif menu_option == "ℹ️ Sobre":
    st.title("🤖 Assistente Ágil IA")
    st.markdown("""
    - Gera Épicos, Features, User Stories e Tasks automaticamente.
    - Feedback visual por etapa de geração com timeline.
    - Exportação pronta para Azure DevOps (CSV/Excel).
    - Integração com Gemini, ChatGPT e Copilot.
    """)

# =====================
# GERAÇÃO DE ARTEFATOS
# =====================
elif menu_option == "🧠 Geração de Artefatos":
    st.title("🧠 Geração de Artefatos Ágeis")
    contexto = st.text_area("🧩 Contexto do projeto", height=100)
    notas = st.text_area("📝 Notas adicionais (opcional)", height=80)

    modelo_escolhido = st.selectbox("Selecione o Modelo de IA", ["Gemini", "ChatGPT", "Copilot"])

    gerar = st.button("🚀 Gerar Artefatos")

    if gerar:
        if not contexto:
            st.warning("Preencha o contexto do projeto antes de gerar.")
        else:
            resultados = {}
            status_placeholders = {}
            cols = st.columns(4)
            artefatos = ["epic", "feature", "user_story", "task"]

            # Carregar Lottie de loading
            lottie_url = "https://assets4.lottiefiles.com/packages/lf20_usmfx6bp.json"
            lottie_json = load_lottie_url(lottie_url)

            # Criar cards de status
            for i, tipo in enumerate(artefatos):
                with cols[i]:
                    st.markdown(f"### {tipo.upper()}")
                    if lottie_json:
                        #st_lottie(lottie_json, height=80, key=f"lottie_{tipo}")
                        st.info("⏳ Processando...")  # ou st.progress() se quiser barra
                    status_placeholders[tipo] = st.empty()
                    status_placeholders[tipo].info(f"⏳ {tipo.upper()} processando...")

            # Processa cada artefato
            for tipo in artefatos:
                prompt_final = f"{config.get('ia_role','')}\n\n"
                if "playbook_text" in config:
                    prompt_final += f"{config['playbook_text']}\n\n"
                prompt_final += f"{config['prompts'][tipo]}\n\nContexto:\n{contexto}\nNotas:\n{notas}"

                # Chamada IA
                if modelo_escolhido == "Gemini":
                    resposta = gerar_resposta_gemini(prompt_final, config["api_keys"]["gemini"])
                elif modelo_escolhido == "ChatGPT":
                    resposta = gerar_resposta_gpt(prompt_final, config["api_keys"]["chatgpt"])
                else:
                    resposta = gerar_resposta_copilot(prompt_final, config["api_keys"]["copilot"])

                resultados[tipo] = resposta
                status_placeholders[tipo].success(f"✅ {tipo.upper()} gerado!")

            # Mostrar resultados
            for tipo in artefatos:
                st.markdown(f"### {tipo.upper()}")
                st.info(resultados[tipo])

            st.session_state["resultados"] = resultados

# =====================
# EXPORTAÇÃO
# =====================
elif menu_option == "📂 Exportação":
    st.title("📂 Exportar Artefatos")
    if "resultados" not in st.session_state:
        st.warning("Gere os artefatos antes de exportar.")
    else:
        df = exportar_artefatos(st.session_state["resultados"])
        st.dataframe(df)

        excel_buffer = baixar_excel(df)
        st.download_button(
            label="📥 Baixar Excel",
            data=excel_buffer,
            file_name="artefatos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
