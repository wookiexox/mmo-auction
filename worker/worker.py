import time
import json
import rabbitmq
from database import SessionLocal
import models


print("Worker started, waiting for rabbitmq")

def process_purchase(ch, method, properties, body):
    data = json.loads(body)
    item_id = data.get("item_id")
    user_id = data.get("user_id")

    print(f"[X] Received request for item '{item_id}' from user '{user_id}'")

    if item_id <= 0 or item_id is None:
        print(f"[!] Error: Item ID {item_id} is invalid, sending to DLQ")
        ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
        return

    db = SessionLocal()
    try:
        item = db.query(models.Item).filter(models.Item.id == item_id).with_for_update().first()
        if not item:
            print(f"[!] Item '{item_id}' not found")
            ch.basic_ack(delivery_tag = method.delivery_tag)
            return
        if item.is_sold:
            print(f"[-] Item '{item_id}' is already sold - user's '{user_id}' transaction failed")
        else:
            print(f"[..] User '{user_id}' is processing payment for item '{item_id}'")
            time.sleep(5)
            item.is_sold = True
            item.owner_id = user_id
            db.commit()
            print(f"[+] Item '{item_id}' purchased successfully by user '{user_id}'")
        ch.basic_ack(delivery_tag = method.delivery_tag)
    except Exception as e:
        print(f"[!] Error: {e}")
        db.rollback()
        ch.basic_nack(delivery_tag = method.delivery_tag, requeue=False)
    finally:
        db.close()

def start_consuming():
    connection = rabbitmq.get_connection()
    channel = rabbitmq.get_channel(connection)
    channel.basic_qos(prefetch_count = 1)

    channel.basic_consume(queue = rabbitmq.QUEUE_NAME, on_message_callback = process_purchase)

    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consuming()
