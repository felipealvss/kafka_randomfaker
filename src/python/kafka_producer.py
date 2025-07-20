from datetime import datetime, timedelta
from kafka import KafkaProducer
from dotenv import load_dotenv
from datetime import datetime
from faker import Faker
import logging
import random
import time
import json
import os

# Dados de clientes
from data.base_clientes import CLIENTES_MAP

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Definir intervalo de datas
data_inicio = datetime(2025, 1, 1)
data_fim = datetime(2025, 7, 31)

# Função para criar producer
def criar_kafka_producer(server=os.getenv('KAFKA_SERVER')):

    producer = KafkaProducer(
        bootstrap_servers=server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    return producer

# Função para gerar datas aleatórias
def gerar_data(data_inicio, data_fim):
    """
    Gera uma data e hora aleatória entre data_inicio e data_fim.
    """
    segundos_intervalo = int((data_fim - data_inicio).total_seconds())
    segundos_aleatorios = random.randint(0, segundos_intervalo)
    data_gerada = data_inicio + timedelta(seconds=segundos_aleatorios)

    if data_gerada > data_fim:
        return data_fim  # Se ultrapassar o intervalo, retorne o limite superior

    return data_gerada

# Criar dados fictícios de movimentações bancárias
def gerar_movimentacao_bancaria(clientes_map_param, data_inicio, data_fim):
    fake = Faker()

    # Lista de clientes
    lista_clientes = list(clientes_map_param.keys())

    # Senecionar clientes origem e destino
    seleciona_cliente_origem = random.choice(lista_clientes)
    seleciona_cliente_destino = random.choice(
        [c for c in lista_clientes if c != seleciona_cliente_origem]
    )

    # Define dicionários origem e destino
    dict_dados_origem = clientes_map_param[seleciona_cliente_origem]
    dict_dados_destino = clientes_map_param[seleciona_cliente_destino]

    # Definição de dados aleatórios
    #_id = random.randint(1000, 9999),
    _id = str(fake.uuid4())
    cliente_origem = dict_dados_origem['nome']
    cliente_destino = dict_dados_destino['nome']
    valor = round(random.uniform(10.0, 1000.0), 2)
    #data_hora = datetime.now().isoformat()
    data_hora = gerar_data(data_inicio, data_fim).isoformat()
    tipo = random.choice(['deposito', 'estorno', 'saque', 'transferencia', 'pagamento_boleto'])
    cidade_origem = dict_dados_origem['cidade']
    cidade_destino = dict_dados_destino['cidade']
    dispositivo = random.choice(['mobile', 'web'])

    # Criar dicionário de dados
    movimentacao = {
        'id_transacao': _id,
        'cliente_origem': cliente_origem,
        'cliente_destino': cliente_destino,
        'valor': valor,
        'data_hora': data_hora,
        'tipo': tipo,
        'status': 'pendente',
        'cidade_origem': cidade_origem,
        'cidade_destino': cidade_destino,
        'dispositivo': dispositivo,
        'categoria_transacao': 'indefinido'
    }

    # Realizar ações
    '''
    Deposito: Adicionar saldo atual do cliente
    Estorno: Adicionar valor ao saldo do cliente de origem
    Saque: Subtrair valor do saldo do cliente, se houver saldo suficiente
    Transferencia: Subtrair valor do cliente de origem e adicionar ao cliente de destino, se houver saldo suficiente
    Pagamento de Boleto: Subtrair valor do saldo do cliente, se houver saldo suficiente
    '''
    if tipo == 'deposito': # Realizar deposito
        movimentacao['cliente_destino'] = 'N/A'
        movimentacao['cidade_destino'] = 'N/A'
        dict_dados_origem['saldo'] += valor
        movimentacao['status'] = 'aprovado'
        movimentacao['categoria_transacao'] = random.choice(['transferencia', 'rendimento', 'pagamento_servico'])
    elif tipo == 'estorno': # Estornar uma transação
        dict_dados_origem['saldo'] += valor
        dict_dados_destino['saldo'] -= valor
        movimentacao['status'] = 'aprovado'
        movimentacao['categoria_transacao'] = random.choice(['reembolso', 'devolucao', 'cancelamento_pagamento'])
    elif tipo == 'saque': # Realizar saque
        movimentacao['cliente_destino'] = 'N/A'
        movimentacao['cidade_destino'] = 'N/A' 
        if dict_dados_origem['saldo'] >= valor:
            dict_dados_origem['saldo'] -= valor
            movimentacao['status'] = 'aprovado'
            movimentacao['categoria_transacao'] = random.choice(['saque_caixa', 'saque_terminal', 'resgate_pontos'])
        else:
            movimentacao['status'] = 'recusado_saldo_insuficiente'
    elif tipo == 'transferencia': # Realizar transferencia
        if dict_dados_origem['saldo'] >= valor:
            dict_dados_origem['saldo'] -= valor
            dict_dados_destino['saldo'] += valor
            movimentacao['status'] = 'aprovado'
            movimentacao['categoria_transacao'] = random.choice(['ted', 'doc', 'pix'])
        else:
            movimentacao['status'] = 'recusado_saldo_insuficiente'
    elif tipo == 'pagamento_boleto': # Realizar pagamento de boleto
        movimentacao['cliente_destino'] = 'N/A'
        movimentacao['cidade_destino'] = 'N/A' 
        if dict_dados_origem['saldo'] >= valor:
            dict_dados_origem['saldo'] -= valor
            movimentacao['status'] = 'aprovado'
            movimentacao['categoria_transacao'] = random.choice(['pagamento_conta', 'pagamento_fatura', 'pagamento_servico'])
        else:
            movimentacao['status'] = 'recusado_saldo_insuficiente'

    return movimentacao

# Função para criar lista com movimentações bancárias
def criar_lista_movimentacoes(clientes_map_param, data_inicio, data_fim, lista=10):
        movimentacoes = [gerar_movimentacao_bancaria(clientes_map_param, data_inicio, data_fim) for _ in range(lista)]
        return movimentacoes

# Realizar envio de dados para o Kafka
def enviar_dados_kafka(clientes_map_param, producer, topic=os.getenv('KAFKA_TOPIC')):

    # Adicionar loop com while True
    while True: 
        movimentacao = criar_lista_movimentacoes(clientes_map_param, data_inicio, data_fim)

        for m in movimentacao:
            try:
                producer.send(topic, m)
                logger.info(f'✅ Dados enviados: {m}')
            except Exception as e:
                logger.error(f'❌ Erro ao enviar dados para o Kafka: {e}')

        producer.flush()

        # Gerar intervalo de envio
        time.sleep(10)

# Função main para iniciar o processo
if __name__ == "__main__":
    producer = criar_kafka_producer()
    enviar_dados_kafka(CLIENTES_MAP, producer)
    producer.close()
