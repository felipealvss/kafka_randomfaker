FROM python:3.10-slim

# Define variáveis de ambiente para o Poetry
ENV POETRY_VERSION=2.0.1 \ # Versão do Poetry
    POETRY_HOME="/opt/poetry" \ # Local de instalação do Poetry
    POETRY_VIRTUALENVS_IN_PROJECT=true \ # Cria o .venv dentro do diretório do projeto
    POETRY_NO_INTERACTION=1 \ # Desabilita prompts interativos durante a instalação do Poetry
    PATH="$POETRY_HOME/bin:$PATH" \ # Adiciona o Poetry ao PATH
    # Variáveis de ambiente para Python (opcionais, mas boas práticas)
    PYTHONDONTWRITEBYTECODE=1 \ # Evita a criação de arquivos .pyc
    PYTHONUNBUFFERED=1 # Garante que stdout/stderr não sejam bufferizados

# Instala o Poetry e dependências de build do sistema (necessárias para alguns pacotes Python)
# build-essential para compilar dependências como psycopg2, numpy etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install "poetry==$POETRY_VERSION" && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de configuração do Poetry primeiro para aproveitar o cache do Docker
# Se pyproject.toml ou poetry.lock não mudarem, essa camada não será reconstruída.
COPY pyproject.toml poetry.lock* ./

# Instala as dependências do projeto usando Poetry
# --no-root: não instala o projeto em si como um pacote Python
# --only main: instala apenas as dependências "main", ignorando as de desenvolvimento (se houver)
# Adicione --no-cache-dir para evitar o cache de pip dentro do container, economizando espaço
RUN poetry install --no-root --only main --no-cache-dir

# Copia o restante do código da aplicação para o diretório de trabalho
# Isso inclui todos os seus scripts em src/
COPY src ./src
COPY .env.example ./ # Copia o arquivo .env. ATENÇÃO: Ver notas sobre segurança abaixo!

# Expõe a porta que o Streamlit usará (essencial para acesso externo ao dashboard)
EXPOSE 8501

# Comando padrão para iniciar a aplicação
# Este CMD será executado quando o container for iniciado sem um comando explícito no docker-compose.yml
# Ele irá rodar o seu main.py, que por sua vez orquestra o Producer, Consumer e Streamlit.
CMD ["poetry", "run", "python", "src/main.py"]
