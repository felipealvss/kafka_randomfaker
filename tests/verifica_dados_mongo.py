from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging

# Configuração do logging para ver mensagens do PyMongo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

def get_mongo_collection():
    """
    Conecta ao MongoDB usando variáveis de ambiente e retorna o objeto da collection.
    """
    mongo_username = os.getenv('MONGO_USERNAME')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_host = os.getenv('MONGO_HOST')
    mongo_port = int(os.getenv('MONGO_PORT')) # Converte para inteiro
    mongo_database = os.getenv('MONGO_DATABASE')
    mongo_collection_name = os.getenv('MONGO_COLLECTION')

    try:
        # Conecta ao MongoDB
        # Se você estiver usando autenticação, o formato da URI pode ser:
        # f"mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/"
        client = MongoClient(mongo_host, mongo_port,
                             username=mongo_username, password=mongo_password)

        # Seleciona o banco de dados
        db = client[mongo_database]

        # Seleciona a collection
        collection = db[mongo_collection_name]

        logger.info(f"✅ Conexão ao MongoDB e collection '{mongo_collection_name}' estabelecida com sucesso!")
        return collection

    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB ou selecionar collection: {e}")
        return None

def fetch_all_documents(collection):
    """
    Busca e imprime todos os documentos de uma collection do MongoDB.
    """
    if collection is None:
        logger.error("A collection não foi inicializada. Não é possível buscar documentos.")
        return

    logger.info(f"\n--- Buscando todos os documentos da collection '{collection.name}' ---")
    try:
        # Realiza a query para buscar todos os documentos
        documents = collection.find({}) # O argumento vazio {} significa "todos os documentos"

        count = 0
        for doc in documents:
            logger.info(f"📄 Documento: {doc}")
            count += 1
        
        if count == 0:
            logger.info("Nenhum documento encontrado na collection.")
        else:
            logger.info(f"Total de {count} documentos encontrados.")

    except Exception as e:
        logger.error(f"❌ Erro ao buscar documentos: {e}")

if __name__ == "__main__":
    collection = get_mongo_collection()
    if collection is not None:
        fetch_all_documents(collection)
        # É uma boa prática fechar a conexão do cliente quando não for mais necessária
        collection.database.client.close()
        logger.info("Conexão com o MongoDB fechada.")