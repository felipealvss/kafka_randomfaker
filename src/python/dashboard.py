from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
import logging
import plotly.express as px

# Configuração do logging para ver mensagens do PyMongo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# ====== CONFIGURAÇÕES GERAIS ======
st.set_page_config(page_title="Monitoramento de transações bancárias", layout="wide")
st.title("📊 Monitoramento de transações bancárias")

# ====== CONEXÃO AO MONGODB ======

def get_mongo_collection():
    """
    Conecta ao MongoDB usando variáveis de ambiente e retorna o objeto da collection.
    """
    mongo_username = os.getenv('MONGO_USERNAME')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_host = os.getenv('MONGO_HOST', 'localhost')  # Definindo um padrão caso não seja especificado
    mongo_port = int(os.getenv('MONGO_PORT', 27017))  # Definindo a porta padrão do MongoDB
    mongo_database = os.getenv('MONGO_DATABASE')
    mongo_collection_name = os.getenv('MONGO_COLLECTION')

    try:
        # Conecta ao MongoDB
        client = MongoClient(mongo_host, mongo_port, username=mongo_username, password=mongo_password)

        # Seleciona o banco de dados
        db = client[mongo_database]

        # Seleciona a collection
        collection = db[mongo_collection_name]

        logger.info(f"✅ Conexão ao MongoDB e collection '{mongo_collection_name}' estabelecida com sucesso!")

        # Exibe resultado de conexão no Streamlit
        st.success(f"Conexão ao MongoDB e collection '{mongo_collection_name}' estabelecida com sucesso!")

        return collection

    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB ou selecionar collection: {e}")

        # Exibe erro no Streamlit
        st.error(f"Erro ao conectar ao MongoDB: {e}")

        return None

def fetch_all_documents(collection):
    """
    Busca todos os documentos de uma collection do MongoDB.
    """
    if collection is None:
        logger.error("A collection não foi inicializada. Não é possível buscar documentos.")
        return []

    logger.info(f"\n--- Buscando todos os documentos da collection '{collection.name}' ---")
    try:
        # Realiza a query para buscar todos os documentos
        documents = collection.find({})  # O argumento vazio {} significa "todos os documentos"

        # Exibe no Streamlit total de documentos encontrados
        count = collection.count_documents({})
        logger.info(f"Total de {count} documentos encontrados.")
        st.info(f"Total de {count} documentos encontrados na collection '{collection.name}'.")

        # Retorna os documentos como uma lista
        return list(documents)

    except Exception as e:
        logger.error(f"❌ Erro ao buscar documentos: {e}")
        return []

# ====== FUNÇÃO PRINCIPAL ======
def main():

    # Botão atualizar
    if st.button("🔄 Atualizar agora"):
        st.cache_data.clear()
        st.rerun()
    
    # Conecta ao MongoDB e obtém a collection
    collection = get_mongo_collection()

    # Busca todos os documentos da collection
    documents = fetch_all_documents(collection)

    st.divider()

    st.subheader("📦 Dados MongoDB")

    # Exibe os dados no Streamlit
    if documents:
        # # Remove o campo _id do MongoDB
        # for doc in documents:
        #     doc.pop('_id', None)

        # Converte em DataFrame
        df = pd.DataFrame(documents)

        # --- 1. Transações por Tipo ---
        st.subheader("📊 Transações por Tipo")
        transacoes_por_tipo = pd.Series([doc['tipo'] for doc in documents]).value_counts()
        st.bar_chart(transacoes_por_tipo)

        # --- 2. Total de Movimentações por Cliente ---
        st.subheader("💰 Total de Movimentações por Cliente")
        movimentacoes_por_cliente = pd.Series([doc['cliente_origem'] for doc in documents]).value_counts()
        movimentacoes_por_cliente_valor = {}
        for cliente in movimentacoes_por_cliente.index:
            movimentacoes_por_cliente_valor[cliente] = sum([doc['valor'] for doc in documents if doc['cliente_origem'] == cliente])
        
        movimentacoes_df = pd.DataFrame(list(movimentacoes_por_cliente_valor.items()), columns=["Cliente", "Valor Total Movimentado"])
        st.dataframe(movimentacoes_df)

        # --- 3. Transações Recusadas ---
        st.subheader("🚫 Transações Recusadas")
        transacoes_recusadas = [doc for doc in documents if doc['status'] == 'recusado_saldo_insuficiente']
        if transacoes_recusadas:
            st.write(f"Total de {len(transacoes_recusadas)} transações recusadas.")
            st.dataframe(pd.DataFrame(transacoes_recusadas).drop(columns=['_id']))
        else:
            st.write("Não há transações recusadas.")

        # --- 4. Detalhamento de Transações ---
        st.subheader("🔍 Detalhamento de Transações")
        selected_transacao = st.selectbox("Selecione uma transação", [f"ID: {doc['id_transacao']}" for doc in documents])
        
        if selected_transacao:
            selected_doc = next(doc for doc in documents if f"ID: {doc['id_transacao']}" == selected_transacao)
            st.write(f"ID: {selected_doc['id_transacao']}")
            st.write(f"Cliente origem: {selected_doc['cliente_origem']}")
            st.write(f"Cliente destino: {selected_doc['cliente_destino']}")
            st.write(f"Valor: {selected_doc['valor']}")
            st.write(f"Data/Hora: {selected_doc['data_hora']}")
            st.write(f"Tipo: {selected_doc['tipo']}")
            st.write(f"Status: {selected_doc['status']}")

        # --- 5. Gráficos de Barras ou Pizza ---
        st.subheader("🍰 Gráfico de Distribuição das Transações por Tipo")
        fig = px.pie(values=transacoes_por_tipo.values, names=transacoes_por_tipo.index, title="Distribuição das Transações")
        st.plotly_chart(fig)

        # --- 6. Exportar Relatórios ---
        st.subheader("📥 Exportar Dados")
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df)
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='transacoes_bancarias.csv',
            mime='text/csv',
        )
        
    else:
        st.write("Nenhum documento encontrado ou erro ao conectar ao MongoDB.")

if __name__ == "__main__":
    main()
