import uvicorn
from enum import Enum
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=['*'],
)

# Database setup
Base = declarative_base()

# Enums
# TODO: Dodaj swoje enumy tutaj
# class YourEnum(str, Enum):
#     VALUE1 = "value1"
#     VALUE2 = "value2"

# Database models
# TODO: Dodaj swoje modele tutaj
# class YourModel(Base):
#     __tablename__ = "your_table"
#
#     id = Column(Integer, primary_key=True, index=True)
#     # Dodaj swoje kolumny tutaj

# Pydantic models
# TODO: Dodaj swoje Pydantic modele tutaj
# class YourSchema(BaseModel):
#     field1: str
#     field2: int

# Database connection (ta sama co w Orders API)
DATABASE_URL = "postgresql://postgres:postgres@localhost/api"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def not_found_exception(db_item):
    """Helper function to raise 404 if item not found"""
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

# Routes
@app.get("/")
def root():
    return {"message": "Your new API is running!"}

# TODO: Dodaj swoje endpointy tutaj
# @app.get("/your-endpoint")
# def your_function(db: Session = Depends(get_db)):
#     # Your logic here
#     pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)