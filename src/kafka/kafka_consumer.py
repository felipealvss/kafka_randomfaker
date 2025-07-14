from kafka import KafkaConsumer
from dotenv import load_dotenv
import logging
import json
import os
from mongo.mongodb_connect import MongoDB

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Kafka Consumer
consumer = KafkaConsumer(
    bootstrap_servers=os.getenv('KAFKA_SERVER'),
    auto_offset_reset='earliest',
    enable_auto_commit=False, # modificado para False para ser realizado commit apenas após a inserção no mongodb
    group_id='grupo_processamento_bancario',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Atribuir uma partição específica ao consumidor
consumer.subscribe([os.getenv('KAFKA_TOPIC')])

# Obter o nome da collection
collection_name = os.getenv('MONGO_COLLECTION')

if __name__ == "__main__":

    # Conectar ao MongoDB
    mongodb = MongoDB()

    # Consumir mensagens do Kafka
    for msg in consumer:
        logger.info(f"❗Recebido: {msg.value}")

        # Enviar os dados para o MongoDB
        try:
            mongodb.insert_message(collection_name, msg.value)
            logger.info("✅ Mensagem inserida no MongoDB com sucesso!")
            consumer.commit()  # Confirma o offset manualmente
        except Exception as e:
            logger.info(f"❌ Erro ao inserir no MongoDB: {e}")

    # Fechar a conexão com o MongoDB quando terminar
    mongodb.close()
    # Fechar o consumidor do Kafka
    consumer.close()