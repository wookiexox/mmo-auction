import os
import pika
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "auction_queue"

def get_connection(retries=10, delay=3):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Połączenie z RabbitMQ nie powiodło się. Ponowna próba za {delay}s")
            time.sleep(delay)
    raise Exception("Nie udało połączyć się z RabbitMQ")

def get_channel(connection):
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    return channel
