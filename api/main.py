import pika
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, get_db
import rabbitmq
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "cAPIbara ready"}

@app.post("/setup-demo")
def setup_demo(db: Session = Depends(get_db)):
    if db.query(models.Item).count() == 0:
        item = models.Item(name="Kordelas", price=2000, is_sold=False)
        db.add(item)
        db.commit()
        return {"message": "created Kordelas"}
    return {"message": "Kordelas already exists"}

@app.post("/buy/{item_id}")
def buy_item(item_id: int, user_id: int):
    connection = rabbitmq.get_connection()
    channel = rabbitmq.get_channel(connection)
    message = json.dumps({
        "item_id": item_id,
        "user_id": user_id
    })

    channel.basic_publish(
        exchange = "",
        routing_key = rabbitmq.QUEUE_NAME,
        body = message,
        properties = pika.BasicProperties(
            delivery_mode = 2,
        )
    )

    connection.close()
    return {"message": "Purchase request sent to queue",
            "item_id": item_id,
            "user_id": user_id}
