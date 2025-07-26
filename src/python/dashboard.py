import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import logging
import plotly.express as px
from pymongo import MongoClient
import datetime

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# ====== CONFIGURAÇÕES GERAIS ======
st.set_page_config(page_title="Monitoramento de transações bancárias", layout="wide")
st.title("📊 Monitoramento de transações bancárias")

# ====== CONEXÃO AO MONGODB ======
@st.cache_resource
def get_mongo_collection():
    mongo_username = os.getenv('MONGO_USERNAME')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = int(os.getenv('MONGO_PORT', 27017))
    mongo_database = os.getenv('MONGO_DATABASE')
    mongo_collection_name = os.getenv('MONGO_COLLECTION')

    try:
        client = MongoClient(mongo_host, mongo_port, username=mongo_username, password=mongo_password)
        db = client[mongo_database]
        collection = db[mongo_collection_name]
        logger.info(f"✅ Conexão ao MongoDB e collection '{mongo_collection_name}' estabelecida com sucesso!")
        st.success(f"Conexão ao MongoDB e collection '{mongo_collection_name}' estabelecida com sucesso!")
        return collection
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB ou selecionar collection: {e}")
        st.error(f"Erro ao conectar ao MongoDB: {e}")
        return None

@st.cache_data(ttl=600)
def fetch_all_documents(_collection):
    if _collection is None:
        logger.error("A collection não foi inicializada. Não é possível buscar documentos.")
        return []
    logger.info(f"\n--- Buscando todos os documentos da collection '{_collection.name}' ---")
    try:
        documents = list(_collection.find({}))
        count = len(documents)
        logger.info(f"Total de {count} documentos encontrados.")
        st.info(f"Total de {count} documentos encontrados na collection '{_collection.name}'.")
        return documents
    except Exception as e:
        logger.error(f"❌ Erro ao buscar documentos: {e}")
        return []

# ====== CONFIGURAÇÃO DO GEMINI API ======
gemini_api_key = os.getenv("GENAI_API_KEY")
if not gemini_api_key:
    st.error("Erro: A variável de ambiente GENAI_API_KEY não está definida. Por favor, configure-a no arquivo .env")
    st.stop()

genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# ====== FUNÇÃO PRINCIPAL ======
def main():

    if st.button("🔄 Atualizar agora"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

    collection = get_mongo_collection()
    documents = fetch_all_documents(collection)

    st.divider()

    if documents:
        df = pd.DataFrame(documents)
        # --- CORREÇÃO AQUI: Converter _id para string ---
        if '_id' in df.columns:
            df['_id'] = df['_id'].astype(str)
            
        df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
        df.dropna(subset=['data_hora'], inplace=True)

        geral_col1, geral_col2, geral_col3 = st.columns([1,1,1])

        with geral_col1:
            st.subheader("📈 Informações de Transações")
            total_transacoes = len(documents)
            if 'total_transacoes_anterior' not in st.session_state:
                st.session_state.total_transacoes_anterior = total_transacoes
            delta_transacoes = total_transacoes - st.session_state.total_transacoes_anterior
            st.session_state.total_transacoes_anterior = total_transacoes
            st.metric(label="Total de Transações", value=total_transacoes, delta=f"{delta_transacoes} transações")

            transacoes_por_tipo = df['tipo'].value_counts()
            fig2 = px.pie(
                values=transacoes_por_tipo.values,
                names=transacoes_por_tipo.index,
                title="Distribuição das Transações",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig2.update_traces(textinfo='percent+label')
            fig2.update_layout(template='plotly_dark')
            st.plotly_chart(fig2)

        with geral_col2:
            st.subheader("💰 Transações por Cliente")
            movimentacoes_por_cliente_valor = df.groupby('cliente_origem')['valor'].sum().reset_index()
            movimentacoes_por_cliente_valor.columns = ["Cliente", "Valor Total de Saldo"]

            top3_clientes = movimentacoes_por_cliente_valor.nlargest(3, "Valor Total de Saldo")

            top3_clientes_ajustado = top3_clientes.copy()
            top3_clientes_ajustado["Valor Total de Saldo"] = top3_clientes["Valor Total de Saldo"].apply(lambda x: f"{x:,.2f}")

            st.text(" ")
            st.markdown("💵 TOP 3 Clientes com maior Saldo")
            st.table(top3_clientes_ajustado)

            fig1 = px.bar(
                top3_clientes,
                x='Cliente',
                y='Valor Total de Saldo',
                title="Top 3 Clientes com Maior Saldo",
                orientation='v',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(template='seaborn')
            st.plotly_chart(fig1)

        with geral_col3:
            st.subheader("📆 Transações por Mês")

            transacoes_por_mes_valor = df.groupby(df['data_hora'].dt.to_period('M'))['valor'].sum()
            transacoes_por_mes_count = df.groupby(df['data_hora'].dt.to_period('M')).size()

            top3_mes = transacoes_por_mes_valor.nlargest(3)
            top3_mes_formatado = top3_mes.apply(lambda x: f"{x:,.2f}")

            st.text(" ")
            st.markdown("💵 TOP 3 Meses com Maior Valor Total de Saldo")
            st.table(top3_mes_formatado)

            fig_time = px.line(
                transacoes_por_mes_count,
                x=transacoes_por_mes_count.index.astype(str),
                y=transacoes_por_mes_count.values,
                title="Total de Transações por Mês",
                labels={'x': 'Mês', 'y': 'Total de Transações'}
            )
            fig_time.update_layout(template='plotly_dark')
            st.plotly_chart(fig_time)

            st.markdown("---")
            st.subheader("🔮 Projeção de Transações para o Fechamento de 2025")

            current_year = datetime.datetime.now().year
            monthly_data_2025 = transacoes_por_mes_valor[transacoes_por_mes_valor.index.year == current_year]

            if not monthly_data_2025.empty:
                last_recorded_month_period = monthly_data_2025.index.max()
                last_recorded_month_name = last_recorded_month_period.strftime('%B %Y')

                monthly_data_str = ""
                for period, value in monthly_data_2025.items():
                    monthly_data_str += f"- {period.strftime('%B %Y')}: R$ {value:,.2f}\n"

                current_month_dt = datetime.datetime.now()
                current_month_name = current_month_dt.strftime('%B %Y')

                llm_projection_prompt = f"""
                Você é um analista financeiro especialista em projeções de vendas e transações.
                A seguir, estão os valores totais de transações bancárias para cada mês do ano de {current_year} até {last_recorded_month_name}.

                Dados históricos de {current_year}:
                {monthly_data_str}

                Com base nesses dados, e considerando que o ano ainda não terminou,
                faça uma projeção **otimista, realista e conservadora** do **valor total de transações** para o **fechamento do ano de {current_year}**.
                Considere que o mês atual é {current_month_name}.
                Apresente suas projeções e uma breve justificativa para cada uma,
                além de quaisquer observações sobre as tendências atuais.

                Responda de forma concisa e direta, usando bullet points ou uma pequena tabela para as projeções.
                """

                if st.button("Gerar Projeção Anual com Gemini", key="projecao_anual_llm"):
                    with st.spinner("Gemini gerando projeção anual..."):
                        try:
                            response = gemini_model.generate_content(
                                llm_projection_prompt,
                                generation_config={
                                    "max_output_tokens": 400,
                                    "temperature": 0.5,
                                }
                            )
                            st.subheader("Projeção do Gemini para o Fechamento de 2025:")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Erro ao gerar projeção com Gemini: {e}")
                            st.warning("Verifique sua chave de API ou se o modelo está acessível.")
            else:
                st.info(f"Dados insuficientes para gerar uma projeção para o ano de {current_year}. Não foram encontradas transações para {current_year}.")


        st.subheader("🚫 Transações Recusadas")
        recusados_col1, recusados_col2 = st.tabs(["📊 Resumo", "📋 Detalhes"])

        transacoes_recusadas_df = df[df['status'] == 'recusado_saldo_insuficiente'].copy()

        if not transacoes_recusadas_df.empty:
            with recusados_col1:
                recusados_col1.markdown(f'## Total de transações recusadas: **{len(transacoes_recusadas_df)}**')
                df_grouped = transacoes_recusadas_df.groupby(['cidade_origem', 'tipo']).size().reset_index(name='total')
                fig_line = px.line(df_grouped,
                                x='cidade_origem',
                                y='total',
                                color='tipo',
                                title='Total de Transações Recusadas por Tipo e Cidade de Origem',
                                labels={'total': 'Total de Transações'},
                                markers=True)
                fig_line.update_layout(template='plotly_dark')
                recusados_col1.plotly_chart(fig_line, use_container_width=True)
            with recusados_col2:
                recusados_col2.dataframe(transacoes_recusadas_df.drop(columns=['_id'], errors='ignore'))
        else:
            recusados_col1.info("Não há transações recusadas para exibir ou analisar.")

        st.subheader("🔍 Detalhamento de Transações")
        if 'id_transacao' in df.columns and not df['id_transacao'].empty:
            selected_transacao_id = st.selectbox(
                "Selecione uma transação pelo ID para ver detalhes:",
                [""] + df['id_transacao'].unique().tolist(),
                index=0
            )

            if selected_transacao_id:
                selected_doc_df = df[df['id_transacao'] == selected_transacao_id].iloc[0]

                try:
                    valor_formatado = float(selected_doc_df['valor'])
                except (ValueError, TypeError):
                    valor_formatado = 0.0

                st.write(f"**ID da Transação:** {selected_doc_df['id_transacao']}")
                st.write(f"**Cliente Origem:** {selected_doc_df['cliente_origem']}")
                st.write(f"**Cliente Destino:** {selected_doc_df['cliente_destino']}")
                st.write(f"**Valor:** R$ {valor_formatado:,.2f}")
                st.write(f"**Data/Hora:** {selected_doc_df['data_hora'].strftime('%d/%m/%Y %H:%M:%S')}")
                st.write(f"**Tipo:** {selected_doc_df['tipo']}")
                st.write(f"**Status:** {selected_doc_df['status']}")

                st.markdown("---")
                st.subheader("Análise Detalhada da Transação com Gemini")
                if st.button("Analisar esta Transação com Gemini", key="analisar_transacao_individual_llm"):
                    with st.spinner("Gemini analisando a transação..."):
                        single_tx_prompt = f"""
                        Analise a seguinte transação bancária e forneça um resumo conciso,
                        identifique quaisquer aspectos notáveis ou incomuns e sugira o que isso pode significar.

                        Detalhes da Transação:
                        ID: {selected_doc_df['id_transacao']}
                        Cliente Origem: {selected_doc_df['cliente_origem']}
                        Cliente Destino: {selected_doc_df['cliente_destino']}
                        Valor: R$ {valor_formatado}
                        Data/Hora: {selected_doc_df['data_hora']}
                        Tipo: {selected_doc_df['tipo']}
                        Status: {selected_doc_df['status']}
                        """
                        try:
                            response_single = gemini_model.generate_content(
                                single_tx_prompt,
                                generation_config={
                                    "max_output_tokens": 200,
                                    "temperature": 0.3,
                                }
                            )
                            st.info(response_single.text)
                        except Exception as e:
                            st.error(f"Erro ao analisar transação individual com Gemini: {e}")
                            st.warning("Verifique sua chave de API ou se o modelo está acessível.")
        else:
            st.info("Nenhum ID de transação encontrado para seleção ou DataFrame vazio.")

        st.subheader("📦🤖 Interação com base de dados e IA")
        #expand_export = st.expander("💻 Interação com base de dados")
        #dados_col1, dados_col2, dados_col3 = expand_export.tabs(["📋 Dados", "🤖 Perguntas com IA", "📥 Download CSV"])
        dados_col1, dados_col2, dados_col3 = st.tabs(["📑 Dados gerais", "🤖 Converse com IA", "📥 Exportar base CSV"])

        @st.cache_data
        def convert_df(df_to_convert):
            df_ajustado = df_to_convert.drop('_id', axis=1)
            return df_ajustado.to_csv(index=False).encode('utf-8')

        with dados_col1:
            st.dataframe(df) # Exibe o DataFrame com _id já convertido para string

        with dados_col2:
            st.markdown("Faça uma pergunta sobre os dados da tabela. A IA tentará extrair insights.")
            
            user_question = st.text_area("Sua pergunta:", key="user_llm_question_tab")

            if st.button("Obter Resposta com Gemini", key="ask_llm_button_tab"):
                if user_question:
                    with st.spinner("Gemini pensando na sua pergunta..."):
                        try:
                            # Prepara o esquema dos dados
                            data_schema = """
                            Estrutura do DataFrame (colunas e seus tipos/exemplos de valores):
                            - _id: String (ID interno do MongoDB, e.g., '687c6eedb7d525d1973c79e8')
                            - id_transacao: String (ID único da transação, e.g., '867a1cfa-7a9b-4f7e-b114-b0392e6483ad')
                            - cliente_origem: String (Nome do cliente de origem, e.g., 'Maria', 'Carlos')
                            - cliente_destino: String (Nome do cliente de destino, e.g., 'N/A', 'Carlos')
                            - valor: Numérico (Float/Decimal, valor da transação, e.g., 422.73, 271.21)
                            - data_hora: Datetime (Timestamp da transação, e.g., '2025-03-21 14:54:57')
                            - tipo: String (Tipo de transação, e.g., 'deposito', 'transferencia', 'saque')
                            - status: String (Status da transação, e.g., 'aprovado', 'recusado_saldo_insuficiente')
                            - cidade_origem: String (Cidade do cliente de origem, e.g., 'São Paulo', 'Belo Horizonte')
                            - cidade_destino: String (Cidade do cliente de destino, e.g., 'Minas Gerais', 'web')
                            - dispositivo: String (Dispositivo usado, e.g., 'mobile', 'web')
                            - categoria_transacao: String (Categoria da transação, e.g., 'pagamento_boleto', 'doc', 'ted')
                            """
                            
                            # Estatísticas descritivas do DataFrame
                            df_description = df.describe(include='all').to_markdown()

                            # Contagem de transação por cidade
                            df_total_por_cidade_origem = df['cidade_origem'].value_counts().to_markdown()

                            # Média de valor por transação
                            df_agrupa_por_tipo = df.groupby('tipo')['valor'].mean().to_markdown(floatfmt=".2f")

                            # Top 5 clientes com maior valor total de transações
                            df_5_clientes_maior_valor = df.groupby('cliente_origem')['valor'].sum().nlargest(5).to_markdown(floatfmt=".2f")

                            llm_question_prompt = f"""
                            Você é um analista de dados especialista em transações bancárias.
                            Recebi um conjunto de dados e gostaria que você respondesse a uma pergunta.
                            Abaixo, segue a estrutura do DataFrame e as estatísticas descritivas para você entender os dados:

                            Estrutura do DataFrame:
                            ```
                            {data_schema}
                            ```

                            Estatísticas Descritivas do DataFrame:
                            ```
                            {df_description}
                            ```

                            Contagem de Transações por Cidade de Origem:
                            ```
                            {df_total_por_cidade_origem}
                            ```

                            Média do Valor por Tipo de Transação:
                            ```
                            {df_agrupa_por_tipo}
                            ```

                            Top 5 Clientes com Maior Valor Total de Transações:
                            ```
                            {df_5_clientes_maior_valor}
                            ```                            

                            Minha pergunta é: "{user_question}"

                            Com base nestas informações detalhadas, responda à pergunta de forma clara, concisa e objetiva. Se a resposta não puder ser obtida diretamente das informações fornecidas, por favor, indique isso. Priorize os dados apresentados nas agregações e estatísticas ao invés de inferências genéricas. Não invente dados.
                            """

                            response = gemini_model.generate_content(
                                llm_question_prompt,
                                generation_config={
                                    "max_output_tokens": 500,
                                    "temperature": 0.2,
                                }
                            )
                            st.success("Resposta do Gemini:")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Erro ao obter resposta do Gemini: {e}")
                            st.warning("Verifique sua chave de API, conectividade ou se a pergunta é muito complexa para o modelo com os dados fornecidos.")
                else:
                    st.warning("Por favor, digite sua pergunta antes de clicar no botão.")

        with dados_col3:
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