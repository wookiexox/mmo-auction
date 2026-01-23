import os
import pika
import time

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "auction_queue_v2"
DLQ_NAME = "auction_dlq"

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

    channel.queue_declare(queue=DLQ_NAME, durable=True)
    args = {
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": DLQ_NAME
    }
    channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments=args)

    return channel
