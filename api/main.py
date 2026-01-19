from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db

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