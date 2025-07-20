import subprocess
import multiprocessing
import sys

# Produtor de dados Kafka
def run_producer():
    print("--- Iniciando Producer ---")
    subprocess.run([
        "poetry", "run", "python", "src/python/kafka_producer.py"
    ], capture_output=True)

# Consumidor de dados Kafka e Envio ao MongoDB
def run_consumer():
    print("--- Iniciando Consumer ---")
    subprocess.run([
        "poetry", "run", "python", "src/python/kafka_consumer.py"
    ], capture_output=True)

# Aplicação Streamlit para visualização
def run_streamlit():
    print("--- Iniciando Streamlit ---")
    subprocess.run([
        "poetry", "run", "streamlit", "run", "src/python/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"
    ], capture_output=True)

def main():
    # Separando os processos em execuções simultâneas
    producer_process = multiprocessing.Process(target=run_producer)
    consumer_process = multiprocessing.Process(target=run_consumer)
    streamlit_process = multiprocessing.Process(target=run_streamlit)

    # Iniciando os processos
    producer_process.start()
    consumer_process.start()
    streamlit_process.start()

    try:
        producer_process.join()
        consumer_process.join()
        streamlit_process.join()
    except:
        # Encerra processos
        producer_process.terminate()
        consumer_process.terminate()
        streamlit_process.terminate()
        sys.exit(0)
        print("Processos encerrados com sucesso.")
    finally:
        print("\nExecução finalizada.")

if __name__ == "__main__":
    print("Iniciando a aplicação.")
    main()
