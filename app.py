import streamlit as st
import json
from ia_models import gerar_resposta_gemini, gerar_resposta_gpt, gerar_resposta_copilot
from utils import exportar_artefatos, baixar_excel, extrair_texto_ppt
import pandas as pd
import time

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
# MENU LATERAL
# =====================
st.sidebar.title("🤖 Assistente Ágil")
menu_option = st.sidebar.radio(
    "Menu",
    ["🧠 Geração de Artefatos", "⚙️ Configurações de IA", "📂 Exportação", "ℹ️ Sobre"]
)

# =====================
# CONFIGURAÇÕES
# =====================
if menu_option == "🔧 Configurações de IA":
    st.header("Configurações Avançadas da IA")

    # Chaves de API
    st.subheader("API Keys")
    for key in config["api_keys"]:
        config["api_keys"][key] = st.text_input(
            f"{key.upper()} API Key",
            value=config["api_keys"][key],
            type="password"
        )

    # Como a IA deve atuar
    st.subheader("Como a IA deve atuar")
    config["ia_role"] = st.text_area(
        "Descreva como a IA deve atuar (ex: Especialista em Metodologia Ágil, seguindo práticas do playbook fornecido)",
        value=config.get("ia_role", ""),
        height=80
    )

    # Upload do PPT (Playbook ágil)
    arquivo_ppt = st.file_uploader("📄 Upload de Playbook em PPT (opcional)", type=["pptx"])
    if arquivo_ppt:
        texto_ppt = extrair_texto_ppt(arquivo_ppt)
        config["playbook_text"] = texto_ppt
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
    - Feedback visual por etapa de geração.
    - Exportação pronta para Azure DevOps (CSV/Excel).
    - IA configurável como especialista e com referência de playbook.
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

            # Criar cards de status
            for i, tipo in enumerate(artefatos):
                status_placeholders[tipo] = cols[i].empty()
                status_placeholders[tipo].info(f"⏳ {tipo.upper()} processando...")

            # Gerar artefatos
            for tipo in artefatos:
                # Construir prompt final
                prompt_final = f"{config.get('ia_role','')} \n\n"
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

            # Salvar para exportação
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
