import asyncio
import httpx
import pika
import json
import os
from colorama import init

init(autoreset=True)

API_HOST = os.getenv("API_HOST", "localhost")
RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")

API_URL = f"http://{API_HOST}:8000"
QUEUE_NAME = "auction_queue_v2"

async def create_item(client, name):
    try:
        response = await client.post(f"{API_URL}/setup-demo", params={"item_name": name})
        data = response.json()
        item_id = data['item_id']
        print(f"[+] Created item '{name} (ID: {item_id})")
        return item_id
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

async def buy_request(client, item_id, user_id):
    try:
        response = await client.post(f"{API_URL}/buy/{item_id}, params={"user_id": user_id}")
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False

async def attack_concurrency(n_requests = 100):
    print(f"RACE CONDITION")

    async with httpx.AsyncClient() as client:
        item_id = await create_item(client, "Scenario sword")
        if not item_id: return

        print(f"[>] Sending {n_requests} requests")

        tasks = []
        for i in range(1, n_requests + 1):
            tasks.append(buy_request(client, item_id, user_id = 1000 + i))

        results = await asyncio.gather(*tasks)
        print(f"[>] Sent {len(results)} requests")
        await asyncio.sleep(7)

        try:
            response = await client.get(f"{API_URL}/items/{item_id}")
            if response.status_code == 200:
                data = response.json()
                owner = data.get("owner_id")
                is_sold = data.get("is_sold")

                if is_sold and owner:
                    print(f"Item has been sold to user {owner}")
                else:
                    print(f"Item has not been sold")
            else:
                print(f"Unable to receive item status")
        except Exception as e:
            print(f"[!] Error while checking the winner: {e}")

def attack_poison():
    print(f"INJECTION")

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
        channel = connection.channel()

        poison_pills = [
            "not JSON",
            json.dumps({"item_id": "tekst", "user_id": 1}),
            json.dumps({"item_id": 999999999999999, "user_id": 1}),
            json.dumps({"item_id": -1, "user_id": 66}),
            json.dumps({"user_id": 5})
        ]

        for msg in poison_pills:
            channel.basic_publish(
                exchange = "",
                routing_key = QUEUE_NAME,
                body = msg
            )
            print(f"[>] Poison sent")
        connection.close()

    except Exception as e:
        print(f"[!] Error: Connection failed: {e}")

async def main():
    await attack_concurrency(n_requests = 50)
    attack_poison()

if __name__ == "__main__":
    asyncio.run(main())
