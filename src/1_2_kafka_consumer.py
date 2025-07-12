from kafka import KafkaConsumer, TopicPartition
from dotenv import load_dotenv
import json
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Kafka Consumer
consumer = KafkaConsumer(
    bootstrap_servers=os.getenv('KAFKA_SERVER'),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=None,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Atribuir uma partição específica ao consumidor
consumer.subscribe([os.getenv('KAFKA_TOPIC')])

# Consumir mensagens do Kafka
for msg in consumer:
    print(f"Recebido: {msg.value}")
