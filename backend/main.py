import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ImageBase(BaseModel):
    bucket: str
    bucket_original: str
    date: datetime = None
    longitude: int
    latitude: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)] 

@app.post("/images/", status_code=status.HTTP_201_CREATED)
async def create_image(image: ImageBase, db: db_dependancy):
    db_image = models.Image(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
