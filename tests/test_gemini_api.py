import os
import google.generativeai as genai
import streamlit as st # Se for testar no Streamlit
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Carregue sua chave de API de uma variável de ambiente (GENAI_API_KEY)
# Ex: export GENAI_API_KEY="SUA_CHAVE_AQUI"
# Ou diretamente para teste rápido (NÃO FAÇA ISSO EM PRODUÇÃO!)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# --- CORREÇÃO AQUI: Use 'gemini-1.5-flash' em vez de 'gemini-pro' ---
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = "How many 'G's in 'huggingface'?"

try:
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 50,
            "temperature": 0.7,
        }
    )
    print(response.text)
    print("\nTeste realizado com Google Gemini API")

except Exception as e:
    print(f"\nOcorreu um erro ao chamar o modelo Gemini: {e}")
    print("Verifique sua chave de API e os limites de uso.")
    print("Certifique-se de que o modelo 'gemini-1.5-flash' está disponível na sua região.")