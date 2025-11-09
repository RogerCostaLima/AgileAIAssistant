# AgileAI Assistant (Streamlit) - Gemini / GPT

Aplicação Streamlit para gerar Épicos, Features, User Stories e Tasks usando modelos OpenAI (Gemini/GPT).
Permite configurar prompts e (opcionalmente) salvar a chave OpenAI no `config.json`.

## Estrutura
- `app.py` - aplicação principal
- `config.json` - arquivo criado/atualizado pela UI contendo user/password, prompts e (opcionalmente) openai_key
- `requirements.txt` - dependências

## Como usar localmente

1. Clone o repositório:
   ```bash
   git clone <seu-repo>
   cd agileai-assistant
