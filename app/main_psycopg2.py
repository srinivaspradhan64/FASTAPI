from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from starlette.status import HTTP_204_NO_CONTENT

app = FastAPI()

class Post(BaseModel):
        title: str
        content: str
        published: bool = True
        # rating: Optional[int] = None
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


@app.get("/")
async def root():
        return {"message": "Hello World"}

@app.get('/posts')
def get_posts():
        cursor.execute(""" SELECT * FROM posts""")
        posts = cursor.fetchall()
        print(posts)
        return {"data": posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post ):
        cursor.execute("""INSERT INTO posts (title, content, published) 
                        VALUES(%s, %s, %s ) RETURNING * """, (post.title, post.content, post.published))
        new_post = cursor.fetchone()
        conn.commit()
        # post_dict = post.dict()
        # post_dict['id'] = randrange(0,100000000)
        # my_posts.append(post_dict)
        return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
        cursor.execute(""" SELECT * from posts WHERE id = %s;""", str(id))
        post = cursor.fetchone()
        # post = find_post(id)
        if not post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Post with {id} was not found")
        print(post)
        return { "post_detail": post }

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
        cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *; """, str(id))
        del_post = cursor.fetchone()
        conn.commit()
        # index = find_index_post(id)
        # my_posts.pop(index)
        if not del_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail = f"Post with id {id} does not exist")
        print(del_post)
        return Response(status_code=HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
        cursor.execute(""" UPDATE posts SET title = %s, 
                                        content = %s,
                                        published = %s 
                                        WHERE id = %s 
                                        RETURNING * """,
                                        (post.title, 
                                        post.content, 
                                        post.published,
                                        str(id)
                                        ))
        update_post = cursor.fetchone()
        conn.commit()
        if not update_post:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail = f"Post with id {id} does not exist")
        # index = find_index_post(id)
        # post_dict = post.dict()
        # post_dict['id'] = id
        # my_posts[index] = post_dict
        return {"message": update_post}
