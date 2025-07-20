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

    # Exibe os dados no Streamlit
    if documents:

        # Converte em DataFrame
        df = pd.DataFrame(documents)

        # --- Informações gerais iniciais ---

        # Cria colunas para dados gerais
        geral_col1, geral_col2, geral_col3 = st.columns([1,1,1])

        # Coluna 1: Total de Transações
        with geral_col1:
            st.subheader("📈 Informações de Transações")
            total_transacoes = len(documents)

            # Calcular o session state para o total de transações
            if 'total_transacoes_anterior' not in st.session_state:
                st.session_state.total_transacoes_anterior = total_transacoes
            delta_transacoes = total_transacoes - st.session_state.total_transacoes_anterior # Calcular a diferença (novos registros)
            st.session_state.total_transacoes_anterior = total_transacoes # Atualizar o valor no session_state para a próxima execução
            st.metric(label="Total de Transações", value=total_transacoes, delta=f"{delta_transacoes} transações")
            
            transacoes_por_tipo = pd.Series([doc['tipo'] for doc in documents]).value_counts()
            fig2 = px.pie(
                values=transacoes_por_tipo.values, 
                names=transacoes_por_tipo.index, 
                title="Distribuição das Transações",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig2.update_traces(textinfo='percent+label')
            fig2.update_layout(template='plotly_dark')
            st.plotly_chart(fig2)

        # Coluna 2: Total de Saldo por Cliente
        with geral_col2:
            st.subheader("💰 Transações por Cliente")
            movimentacoes_por_cliente = pd.Series([doc['cliente_origem'] for doc in documents]).value_counts()
            movimentacoes_por_cliente_valor = {}
            for cliente in movimentacoes_por_cliente.index:
                movimentacoes_por_cliente_valor[cliente] = sum([doc['valor'] for doc in documents if doc['cliente_origem'] == cliente])
            movimentacoes_df = pd.DataFrame(list(movimentacoes_por_cliente_valor.items()), columns=["Cliente", "Valor Total de Saldo"])
            top3_clientes = movimentacoes_df.nlargest(3, "Valor Total de Saldo")

            # Ajuste de valor na tabela
            top3_clientes_ajustado = top3_clientes.copy()
            top3_clientes_ajustado["Valor Total de Saldo"] = top3_clientes["Valor Total de Saldo"].apply(lambda x: f"{x:,.2f}")

            st.text(" ")
            st.markdown("💵 TOP 3 Clientes com maior Saldo")
            st.table(top3_clientes_ajustado)
            #st.dataframe(movimentacoes_df)

            fig1 = px.bar(
                top3_clientes, 
                x='Cliente', 
                y='Valor Total de Saldo', 
                title="Top 5 Clientes com Maior Saldo",
                orientation='v',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(template='seaborn')
            st.plotly_chart(fig1)

            # Coluna 3: Transações por Mês
            with geral_col3:
                st.subheader("📆 Transações por Mês")
                
                df['data_hora'] = pd.to_datetime(df['data_hora'])

                transacoes_por_mes_valor = df.groupby(df['data_hora'].dt.to_period('M'))['valor'].sum()

                top3_mes = transacoes_por_mes_valor.nlargest(3)

                # Ajuste de valor na tabela
                top3_mes_formatado = top3_mes.apply(lambda x: f"{x:,.2f}")

                # Exibindo a tabela do TOP 1 Mês com Maior Valor Total de Saldo

                st.text(" ")
                st.markdown("💵 TOP 3 Meses com Maior Valor Total de Saldo")
                st.table(top3_mes_formatado)

                # Agrupando por mês e contando o total de transações
                transacoes_por_mes = df.groupby(df['data_hora'].dt.to_period('M')).size()

                # Plotando gráfico de linha para mostrar a evolução mensal
                fig_time = px.line(
                    transacoes_por_mes, 
                    x=transacoes_por_mes.index.astype(str), 
                    y=transacoes_por_mes.values,
                    title="Transações por Mês",
                    labels={'x': 'Mês', 'y': 'Total de Transações'}
                )
                fig_time.update_layout(template='plotly_dark')
                st.plotly_chart(fig_time)

        # --- Transações Recusadas ---
        st.subheader("🚫 Transações Recusadas")

        # Criando abas para agrupamento de informações
        recusados_col1, recusados_col2 = st.tabs(["📊 Resumo", "📋 Detalhes"])

        # Filtrar dataframe por recusados
        transacoes_recusadas = [doc for doc in documents if doc['status'] == 'recusado_saldo_insuficiente']
        # Criar dataframe para transações recusadas
        if transacoes_recusadas:
            # Cria dataframe
            df_transacoes = pd.DataFrame(transacoes_recusadas).drop(columns=['_id'])
            colunas_recusadas = ['id_transacao', 'tipo', 'status', 'cidade_origem']
            df_transacoes_filtrado = df_transacoes[colunas_recusadas]

            # Página 1: Big number em parkdown
            recusados_col1.markdown(f'## Total de transações recusadas: **{len(transacoes_recusadas)}**')
            st.text(" ")
            # Agrupar por "cidade_origem" e "tipo" e contar os totais
            df_grouped = df_transacoes_filtrado.groupby(['cidade_origem', 'tipo']).size().reset_index(name='total')

            # Criar um gráfico de linha
            fig_line = px.line(df_grouped, 
                            x='cidade_origem', 
                            y='total', 
                            color='tipo', 
                            title='Total de Transações por Tipo e Cidade de Origem',
                            labels={'total': 'Total de Transações'},
                            markers=True)

            # Exibir o gráfico
            recusados_col1.plotly_chart(fig_line, use_container_width=True)

            # Página 2: Adicionando tabela resumo     
            recusados_col2.dataframe(df_transacoes_filtrado)
        else:
            recusados_col1.write("Não há transações recusadas.")

        # --- Detalhamento de Transações ---
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

        # --- Exportar Relatórios ---
        st.subheader("📦 Dados MongoDB")

        # Criar expandar para dados gerais
        expand_export = st.expander("📦 Dados gerais")

        # Criar colunas para dados gerais
        dados_col1, dados_col2 = expand_export.tabs(["📋 Dados", "📥 Download CSV"])

        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        # Exibir dados totais do dataframe
        dados_col1.dataframe(df)
        
        # Botão de download CSV
        csv = convert_df(df)
        dados_col2.download_button(
            label="Baixar CSV",
            data=csv,
            file_name='transacoes_bancarias.csv',
            mime='text/csv',
        )
        
    else:
        st.write("Nenhum documento encontrado ou erro ao conectar ao MongoDB.")

if __name__ == "__main__":
    main()
