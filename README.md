# 🚀 Projeto de Simulação de Atividades Bancárias com Kafka, MongoDB e Streamlit

Este projeto simula um pipeline de dados de atividades bancárias usando **Apache Kafka** para transmissão de mensagens, **MongoDB** para armazenamento e **Streamlit** para visualização e análise em tempo real.

**Repositório GitHub:** [https://github.com/felipealvss/kafka\_randomfaker](https://github.com/felipealvss/kafka_randomfaker)

---

## 🌟 Visão Geral

O objetivo principal é demonstrar um fluxo de dados em tempo real:

1. **Geração de Dados Fictícios:** Um `Producer` gera transações bancárias simuladas (depósitos, saques, transferências) com lógica de saldo.
2. **Streaming de Mensagens:** As transações são enviadas para um tópico Kafka.
3. **Consumo e Persistência:** Um `Consumer` lê as mensagens do Kafka e as persiste em um banco de dados MongoDB.
4. **Visualização Analítica:** O Streamlit se conecta ao MongoDB para exibir informações analíticas e insights sobre as movimentações bancárias.

---

## 🛠️ Tecnologias Utilizadas

* **Apache Kafka:** Plataforma de streaming de eventos distribuída.
* **MongoDB:** Banco de dados NoSQL para armazenamento das transações.
* **Streamlit:** Framework Python para construção rápida de aplicações web interativas e dashboards.
* **Python:** Linguagem de programação principal.
* **Docker & Docker Compose:** Para orquestração e execução dos serviços (Kafka, Zookeeper, MongoDB).

---

## 📂 Estrutura do Projeto

```
.
├── docker-compose.yml              # Definição dos serviços Docker (Kafka, Zookeeper, MongoDB)
├── Dockerfile                      # Arquivo para criação da imagem Docker do projeto
├── poetry.lock                     # Bloqueio das dependências do Poetry
├── pyproject.toml                  # Dependências do projeto (utiliza o Poetry)
├── README.md                       # Este arquivo
├── requirements.txt                # Dependências Python (caso não use o Poetry)
└── src/
    ├── dashboard_streamlit.py      # Aplicação Streamlit para visualização das transações
    ├── kafka_consumer.py           # Script para consumir dados do Kafka e persistir no MongoDB
    ├── kafka_producer.py           # Script para gerar e enviar dados para o Kafka
    ├── main.py                     # Script principal para rodar o fluxo do projeto
    ├── mongodb_connect.py          # Módulo para conexão e operações no MongoDB
    └── test
        └── verifica_dados_mongo.py # Script para testar e verificar dados no MongoDB
```

---

## 📊 Visualização no Streamlit

O aplicativo Streamlit (`dashboard_streamlit.py`) se conecta ao MongoDB e fornece um dashboard interativo onde você poderá:

* Ver as últimas transações.
* Visualizar estatísticas agregadas (total de depósitos, saques, etc.).
* Analisar o saldo dos clientes (se implementado no Streamlit).
* Observar o fluxo de dados em tempo real.

---

## 🚀 Como Rodar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/felipealvss/kafka_randomfaker.git
cd kafka_randomfaker
```

### 2. Configurar o Ambiente

Recomenda-se usar o **Poetry** para gerenciar as dependências do projeto:

```bash
poetry install
```

Alternativamente, se preferir usar o `pip`, instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Subir os Serviços com Docker Compose

Este projeto utiliza Docker e Docker Compose para orquestrar os serviços. Execute o seguinte comando para iniciar o Kafka, Zookeeper e o MongoDB:

```bash
docker-compose up -d
```

Isso irá subir os containers com as configurações predefinidas.

### 4. Executar o Kafka Producer

Para gerar transações bancárias e enviá-las para o Kafka, execute o script `kafka_producer.py`:

```bash
python src/kafka_producer.py
```

### 5. Executar o Kafka Consumer

Para consumir as mensagens do Kafka e persistir os dados no MongoDB, execute o script `kafka_consumer.py`:

```bash
python src/kafka_consumer.py
```

### 6. Rodar a Aplicação Streamlit

Para visualizar o dashboard em tempo real, rode a aplicação Streamlit:

```bash
streamlit run src/dashboard_streamlit.py
```

O Streamlit será acessível no navegador através do endereço `http://localhost:8501`.

---

## 🧪 Testes

Os testes podem ser executados com o framework de testes de sua escolha. Um exemplo de teste já está implementado no arquivo `src/test/verifica_dados_mongo.py`, que verifica a persistência dos dados no MongoDB.

Para rodar os testes, você pode usar o `pytest`:

```bash
pytest src/test/verifica_dados_mongo.py
```

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---
