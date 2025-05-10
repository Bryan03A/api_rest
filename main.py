from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from db_connector.connector import Base, SessionLocal, engine

# Model
from sqlalchemy.ext.declarative import declarative_base

class Name(Base):
    __tablename__ = "names"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Dependency to obtain DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/names")
def get_names(db: Session = Depends(get_db)):
    return db.query(Name).all()

@app.post("/names")
def add_name(name: str, db: Session = Depends(get_db)):
    db_name = Name(name=name)
    db.add(db_name)
    db.commit()
    db.refresh(db_name)
    return db_name

@app.delete("/names/{name_id}")
def delete_name(name_id: int, db: Session = Depends(get_db)):
    name = db.query(Name).filter(Name.id == name_id).first()
    if not name:
        raise HTTPException(status_code=404, detail="Name not found")
    db.delete(name)
    db.commit()
    return {"detail": "Deleted"}
