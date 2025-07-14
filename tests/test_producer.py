import pytest
from kafka.kafka_producer import gerar_movimentacao_bancaria

def test_gerar_movimentacao_bancaria():
    # Chama a função para gerar uma movimentação bancária
    movimentacao = gerar_movimentacao_bancaria()

    # Verifica se o tipo de transação é válido
    assert movimentacao['tipo'] in ['deposito', 'saque', 'transferencia'], "Tipo de transação inválido"
    
    # Verifica se o valor está no intervalo correto
    assert 10.0 <= movimentacao['valor'] <= 1000.0, f"Valor fora do intervalo esperado: {movimentacao['valor']}"
    
    # Verifica se a movimentação tem um ID único (não pode ser nulo ou vazio)
    assert movimentacao['id_transacao'], "ID de transação não gerado"

    # Verifica se o cliente origem é válido
    assert movimentacao['cliente_origem'] in ['Davi', 'Maria', 'Felipe', 'Ana', 'Carlos'], "Cliente origem inválido"

    # Verifica se a data e hora foi gerada corretamente (não pode ser vazio)
    assert movimentacao['data_hora'], "Data e hora não gerada"
