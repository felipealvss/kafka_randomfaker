import subprocess
import multiprocessing

# Produtor de dados Kafka
def run_producer():
    print("Iniciando Producer...")
    subprocess.run([
        "poetry", "run", "python", "src/kafka_producer.py"
    ], capture_output=True)

# Consumidor de dados Kafka e Envio ao MongoDB
def run_consumer():
    print("Iniciando Consumer...")
    subprocess.run([
        "poetry", "run", "python", "src/kafka_consumer.py"
    ], capture_output=True)

# Aplicação Streamlit para visualização
def run_streamlit():
    print("Iniciando Streamlit...")
    subprocess.run([
        "poetry", "run", "streamlit", "run", "src/dashboard_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"
    ], capture_output=True)

if __name__ == "__main__":
    # Rodando o producer e o consumer simultaneamente em dois processos separados
    producer_process = multiprocessing.Process(target=run_producer)
    consumer_process = multiprocessing.Process(target=run_consumer)
    streamlit_process = multiprocessing.Process(target=run_streamlit)

    # Iniciando os processos
    producer_process.start()
    consumer_process.start()
    streamlit_process.start()

    # Esperando os dois processos terminarem
    producer_process.join()
    consumer_process.join()
    streamlit_process.join()
