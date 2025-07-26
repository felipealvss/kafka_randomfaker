import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

# --- Configuração da API do Gemini ---
# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da API do Gemini
# Se a chave não for encontrada, o script irá parar e exibir um erro
api_key = os.getenv("GENAI_API_KEY")
if not api_key:
    st.error("Erro: A variável de ambiente GENAI_API_KEY não está definida.")
    st.stop() # Interrompe a execução do Streamlit se a chave não estiver presente

genai.configure(api_key=api_key)

# Inicializar o modelo Gemini
# Usaremos 'gemini-1.5-flash' por sua compatibilidade e bom desempenho
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Interface do Streamlit ---
st.set_page_config(page_title="Interação com Gemini", layout="centered")
st.title("✨ Chat Simples com Google Gemini ✨")

st.markdown(
    """
    Este é um painel simples para interagir com o modelo **Gemini 1.5 Flash**.
    Digite sua pergunta na caixa de texto abaixo e o Gemini irá responder!
    """
)

# Campo de entrada para a pergunta do usuário
user_query = st.text_area(
    "Digite sua pergunta aqui:",
    placeholder="Ex: Qual é a capital da França?",
    height=100
)

# Botão para enviar a pergunta
if st.button("Obter Resposta do Gemini"):
    if user_query:
        # Exibir um spinner enquanto o modelo está pensando
        with st.spinner("Gemini está pensando... 🤔"):
            try:
                # Chamar a API do Gemini
                response = model.generate_content(
                    user_query,
                    generation_config={
                        "max_output_tokens": 150, # Limitar o tamanho da resposta
                        "temperature": 0.7,        # Controlar a criatividade (0.0 a 1.0)
                    }
                )

                # Exibir a resposta do Gemini
                st.subheader("Resposta do Gemini:")
                st.info(response.text) # st.info para destacar a resposta

            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
                st.warning("Por favor, tente novamente ou verifique sua chave de API e os limites de uso.")
    else:
        st.warning("Por favor, digite uma pergunta antes de enviar.")

st.markdown("---")
st.caption("Desenvolvido com Streamlit e Google Gemini API")