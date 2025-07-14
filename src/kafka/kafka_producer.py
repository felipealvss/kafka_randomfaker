from kafka import KafkaProducer
from dotenv import load_dotenv
from datetime import datetime
from faker import Faker
import logging
import random
import time
import json
import os

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Definir clientes e saldos iniciais
base_clientes = {
    'Davi': 1000.0,
    'Maria': 1500.0,
    'Felipe': 2000.0,
    'Ana': 1200.0,
    'Carlos': 800.0
}

# Função para criar producer
def criar_kafka_producer(server=os.getenv('KAFKA_SERVER')):

    producer = KafkaProducer(
        bootstrap_servers=server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

# Criar dados fictícios de movimentações bancárias
def gerar_movimentacao_bancaria(base_clientes):
    fake = Faker()

    # Lista de clientes
    clientes = list(base_clientes.keys())

    # Definição de dados aleatórios
    #_id = random.randint(1000, 9999),
    _id = str(fake.uuid4())
    cliente_origem = random.choice(clientes)
    cliente_destino = random.choice([c for c in clientes if c != cliente_origem])
    valor = round(random.uniform(10.0, 1000.0), 2)
    data_hora = datetime.now().isoformat()
    tipo = random.choice(['deposito', 'saque', 'transferencia'])

    # Criar dicionário de dados
    movimentacao = {
        'id_transacao': f"{_id}",
        'cliente_origem': cliente_origem,
        'cliente_destino': cliente_destino,
        'valor': valor,
        'data_hora': data_hora,
        'tipo': tipo,
        'status': 'sucesso'
    }

    # Realizar ações
    '''
    Deposito: Adicionar saldo atual do cliente
    Saque: Subtrair valor do saldo do cliente, se houver saldo suficiente
    Transferencia: Subtrair valor do cliente de origem e adicionar ao cliente de destino, se houver saldo suficiente
    '''
    if tipo == 'deposito': # Realizar deposito
        base_clientes[cliente_destino] == 'N/A'
        base_clientes[cliente_origem] += valor
        movimentacao['status'] = 'aprovado'
    elif tipo == 'saque': # Realizar saque
        base_clientes[cliente_destino] == 'N/A'
        if base_clientes[cliente_origem] >= valor:
            base_clientes[cliente_origem] -= valor
            movimentacao['status'] = 'aprovado'
        else:
            movimentacao['status'] = 'recusado_saldo_insuficiente'
    elif tipo == 'transferencia': # Realizar transferencia
        if base_clientes[cliente_origem] >= valor:
            base_clientes[cliente_origem] -= valor
            base_clientes[cliente_destino] += valor
            movimentacao['status'] = 'aprovado'
        else:
            movimentacao['status'] = 'recusado_saldo_insuficiente'

    return movimentacao

# Função para criar lista com movimentações bancárias
def criar_lista_movimentacoes(lista=10):
        movimentacoes = [gerar_movimentacao_bancaria() for _ in range(lista)]
        return movimentacoes

# Realizar envio de dados para o Kafka
def enviar_dados_kafka(producer, topic=os.getenv('KAFKA_TOPIC')):

    # Adicionar loop com while True
    while True: 
        movimentacao = criar_lista_movimentacoes()

        for m in movimentacao:
            try:
                producer.send(topic, m)
                logger.info(f'✅ Dados enviados: {m}')
            except Exception as e:
                logger.info(f'❌ Erro ao enviar dados para o Kafka: {e}')

        producer.flush()

        # Gerar intervalo de envio
        time.sleep(10)

# Função main para iniciar o processo
if __name__ == "__main__":
    producer = criar_kafka_producer()
    enviar_dados_kafka(producer)
    producer.close()
