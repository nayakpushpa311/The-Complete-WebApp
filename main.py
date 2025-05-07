from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Define SQLAlchemy models
Base = declarative_base()


class PersonDB(Base):
    __tablename__ = "people"
    # Using __tablename__ is a convention that SQLAlchemy follows to map Python class attributes to database table columns and to specify the table name in the database schema.
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)


# Set up SQLite database
DATABASE_URL = "sqlite:///C:/Users/prath/Downloads/API/API/mydb.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if not already created)
Base.metadata.create_all(bind=engine)


# Pydantic model for request data
class Person(BaseModel):
    id: int
    name: str
    age: int
    gender: str


# CRUD operations
@app.post("/people/", response_model=Person)
def create_person(person: Person):
    db_person = PersonDB(**person.dict())
    with SessionLocal() as session:
        session.add(db_person)
        session.commit()
        session.refresh(db_person)
    return db_person


@app.get("/people/{person_id}", response_model=Person)
def read_person(person_id: int):
    with SessionLocal() as session:
        person = session.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        return person


@app.put("/people/{person_id}", response_model=Person)
def update_person(person_id: int, updated_person: Person):
    with SessionLocal() as session:
        person = session.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        for attr, value in updated_person.dict().items():
            setattr(person, attr, value)
        session.commit()
        session.refresh(person)
        return person


@app.delete("/people/{person_id}", response_model=Person)
def delete_person(person_id: int):
    with SessionLocal() as session:
        person = session.query(PersonDB).filter(PersonDB.id == person_id).first()
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        session.delete(person)
        session.commit()
        return person


@app.get("/people/", response_model=List[Person])
def get_people():
    with SessionLocal() as session:
        people = session.query(PersonDB).all()
        return people

