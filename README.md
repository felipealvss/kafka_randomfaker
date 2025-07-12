
# 🚀 Projeto de Simulação de Atividades Bancárias com Kafka, MongoDB e Streamlit

Este projeto simula um pipeline de dados de atividades bancárias usando **Apache Kafka** para transmissão de mensagens, **MongoDB** para armazenamento e **Streamlit** para visualização e análise em tempo real.

-----

## 🌟 Visão Geral

O objetivo principal é demonstrar um fluxo de dados em tempo real:

1.  **Geração de Dados Fictícios:** Um `Producer` gera transações bancárias simuladas (depósitos, saques, transferências) com lógica de saldo.
2.  **Streaming de Mensagens:** As transações são enviadas para um tópico Kafka.
3.  **Consumo e Persistência:** Um `Consumer` lê as mensagens do Kafka e as persiste em um banco de dados MongoDB.
4.  **Visualização Analítica:** O Streamlit se conecta ao MongoDB para exibir informações analíticas e insights sobre as movimentações bancárias.

-----

## 🛠️ Tecnologias Utilizadas

  * **Apache Kafka:** Plataforma de streaming de eventos distribuída.
  * **MongoDB:** Banco de dados NoSQL para armazenamento das transações.
  * **Streamlit:** Framework Python para construção rápida de aplicações web interativas e dashboards.
  * **Python:** Linguagem de programação principal.
  * **Docker & Docker Compose:** Para orquestração e execução dos serviços (Kafka, Zookeeper, MongoDB).

-----

## 📂 Estrutura do Projeto (Exemplo)

```
.
├── .env                            # Variáveis de ambiente (credenciais, hosts, tópicos)
├── docker-compose.yml              # Definição dos serviços Docker (Kafka, Zookeeper, MongoDB)
├── src/
    ├── tests/
    │   └── verifica_dados_mongo.py # Script para verificar dados no MongoDB
│   ├── kafka_producer.py           # Script para gerar e enviar dados para o Kafka
│   ├── kafka_consumer.py           # Script para consumir dados do Kafka e enviar para o MongoDB
│   ├── mongodb_connect.py          # Módulo para conexão e operações no MongoDB
│   └── streamlit_app.py            # Aplicação Streamlit para visualização
├── README.md                       # Este arquivo
└── requirements.txt                # Dependências Python (ou pyproject.toml se usar Poetry)
```
-----

## 📊 Visualização no Streamlit

O aplicativo Streamlit (`streamlit_app.py`) se conectará ao MongoDB e fornecerá um dashboard onde você poderá:

  * Ver as últimas transações.
  * Visualizar estatísticas agregadas (total de depósitos, saques, etc.).
  * Analisar o saldo dos clientes (se implementado no Streamlit).
  * Observar o fluxo de dados em tempo real.

-----
