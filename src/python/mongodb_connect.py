import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carregar as variáveis de ambiente
load_dotenv()

class MongoDB:
    def __init__(self):

        mongo_username = os.getenv('MONGO_USERNAME')
        mongo_password = os.getenv('MONGO_PASSWORD')
        mongo_host = os.getenv('MONGO_HOST')
        mongo_port = os.getenv('MONGO_PORT')
        mongo_database = os.getenv('MONGO_DATABASE')

        # Conexão URI do MongoDB
        self.mongo_uri = f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_database}?authSource=admin"

        # Conectar ao MongoDB
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[mongo_database]

    def insert_message(self, collection_name, message_data):
        """ Insere uma mensagem na coleção especificada """
        collection = self.db[collection_name]
        collection.insert_one(message_data)

    def close(self):
        """ Fecha a conexão com o MongoDB """
        self.client.close()
