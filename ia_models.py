import google.generativeai as genai
import openai
import requests

# =====================
# GEMINI
# =====================
def gerar_resposta_gemini(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        modelos_disponiveis = [
            m.name for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        if not modelos_disponiveis:
            return "[Gemini] Nenhum modelo disponível para generateContent."
        
        model_name = modelos_disponiveis[0]
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[Gemini] ERRO: {e}"

# =====================
# CHATGPT
# =====================
def gerar_resposta_gpt(prompt, api_key, model="gpt-4o-mini"):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ChatGPT] ERRO: {e}"

# =====================
# COPILOT
# =====================
def gerar_resposta_copilot(prompt, api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"input": prompt}
        response = requests.post(
            "https://api.githubcopilot.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"[Copilot] ERRO: {response.text}"
    except Exception as e:
        return f"[Copilot] ERRO: {e}"
