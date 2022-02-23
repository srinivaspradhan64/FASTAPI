# from typing import Optional,List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from passlib.context import CryptContext
# from pydantic import BaseModel
# from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy.orm.session import Session
# from sqlalchemy.orm import Session
# from sqlalchemy.sql.functions import mode
from . import models, schemas, utils
from .database import engine, get_db
# from starlette.status import HTTP_204_NO_CONTENT
from .routers import post, user, auth

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()



while True: 
        try:
                conn = psycopg2.connect(host = 'localhost',
                                database = 'fastapi', 
                                user='postgres', 
                                password='pass',
                                cursor_factory=RealDictCursor
                                )
                cursor = conn.cursor()
                print("Database connection was successful!")
                break
        except Exception as error:
                print("Connecting to database failed.")
                print(f"Error was {error}")
                time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
                {"title": "favourite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
        for p in my_posts:
                if p["id"] == id:
                        return p

def find_index_post(id):
        for i , p in enumerate(my_posts):
                if p['id'] == id:
                        return i

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
        return {"message": "Hello World"}

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)