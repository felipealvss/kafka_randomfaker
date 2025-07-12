import subprocess

def run_producer():
    print("Iniciando Producer...")
    subprocess.run([
        "python", "src/kafka_producer.py"
    ])

def run_consumer():
    print("Iniciando Consumer...")
    subprocess.run([
        "python", "src/kafka_consumer.py"
    ])

if __name__ == "__main__":
    run_producer()        # Gera e envia dados para o Kafka
    run_consumer()        # Consome dados do Kafka e envia para o MongoDB
