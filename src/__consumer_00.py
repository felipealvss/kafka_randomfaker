from kafka import KafkaConsumer, TopicPartition
import json

consumer = KafkaConsumer(
            
            # NOME DO TOPICO, MESMO DO PRODUCER
            #'meu_topico_tickets',
            
            # LOCAL ONDE ESTA O TÓPICO QUE O CONSUMER IRÁ ESCUTAR
            bootstrap_servers='localhost:9092',
            
            # CASO AINDA NAO TENHA OFFSET REGISTRADO:
            # Com 'earliest', ele começa do início do log, lendo todas as mensagens disponíveis.
            # Com 'latest', ele começa apenas a partir das mensagens novas que chegarem depois da conexão.
            auto_offset_reset='earliest', # inicio ou latest fim

            # o Kafka salva esse offset automaticamente em um tópico interno chamado __consumer_offsets
            enable_auto_commit=True,

            # define o grupo ao qual esse consumidor pertence
            # Voce tem um grupo de testes... recebendo mensagens de teste... dai voce vira a chave... passa ao grupo de producao... para nao pegar as mensagens do teste
            # voce deixa como LATEST
            group_id='grupo1',

            value_deserializer=lambda x: json.loads(x.decode('utf-8')),

            #consumer_timeout_ms=30000 # X segundos para verificar o topico com novas mensagens

        )

# Vamos assumir que você quer saber o offset de um tópico específico:
particao = TopicPartition('movimentacoes', 0)
consumer.assign([particao])
# Pega o offset atual salvo:
posicao_atual = consumer.position(particao)
print(f"Offset atual salvo para o grupo: {posicao_atual}\n")


print("🟢 Ouvindo o tópico Kafka...")
print("Aguardando mensagens...")

for msg in consumer:
    print(f"Recebido: {msg.value}")

# MAIS DE ALGUMAS COISAS...

# if __name__ == "__main__":
#     c = KafkaTktConsumidor()
#     c.consumidor()

# consumer = KafkaConsumer(
#     'meu_topico_tickets',
#     bootstrap_servers='localhost:9092',
#     auto_offset_reset='earliest', # inicio ou latest fim
#     enable_auto_commit=True,
#     group_id='grupo_' + str(int(time.time())),
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )

# consumer = KafkaConsumer(
#     'meu_topico_tickets',
#     bootstrap_servers='localhost:9092',
#     auto_offset_reset='earliest', # inicio ou latest fim
#     enable_auto_commit=False,
#     group_id='grupo_' + str(int(time.time())),
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )

# for i, msg in enumerate(consumer):
#     print(f"Recebido: {msg.value}")
#     if i == 4:  # lê no máximo 5 mensagens
#         break
