FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Instala Poetry
ENV POETRY_VERSION=2.0.1
RUN pip install "poetry==$POETRY_VERSION"

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY pyproject.toml poetry.lock* ./
COPY src ./src
COPY requirements.txt ./

# Instala dependências do projeto
RUN poetry install --no-root --only main

# Copia demais arquivos (se necessário)
COPY . .

# Define variável de ambiente para não criar arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Define variável de ambiente para não criar diretórios __pycache__
ENV PYTHONUNBUFFERED=1

# Exemplo de entrypoint (ajuste conforme seu script principal)
CMD ["poetry", "run", "python", "src/main.py"]
