from random import randrange
import time
from tkinter.messagebox import NO 
from tkinter.tix import Tree
from turtle import title
from xmlrpc.client import Boolean
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import  RealDictCursor
from requests import Response
class Post(BaseModel):
    title: str
    content: str
    published: Boolean = False

while True:
    try:
        connection = psycopg2.connect('postgres://postgres:postgrespw@localhost:55001',cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print('connection to db !!!')
        break
    except Exception as error:
        print('connection to db failed', error)
        time.sleep(2)
posts_data = [{"title": "beaches in Toronto", "content": " lake view", "id": 1}, {
        "title": "beaches in canada", "content": " lake view", "id": 2}]


def find_post_by_id(id: int):
    for i, post in enumerate(posts_data):
        if post['id'] == id:
            return i
    return -1


app = FastAPI()


@app.get("/")
async def root():
    return {"posts": posts_data}


@app.get("/posts")
def all_posts():
    cursor.execute("Select * from posts")
    posts = cursor.fetchall()
    return {"posts": posts}


@app.get("/posts/{id}")
def post_by_id(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s",(id,))
    post  = cursor.fetchone()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                        detail=f'post with {id} not found !!!')
    else:
        return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def new_post(data: Post):

    cursor.execute("""
    INSERT INTO posts(title, content, published) VALUES(%(title)s, %(content)s, %(published)s) RETURNING *
    """, 
    {'title' :data.title, 'content': data.content, 'published':data.published}
    )
    new_post = cursor.fetchone()
    connection.commit()
    return {"new post created": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_by_id(id: int):
    cursor.execute("DELETE FROM  posts WHERE id = %s RETURNING * ",(id,))
    deleted_post = cursor.fetchone()
    connection.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found!!')
    return Response()


@app.put("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post(id: int, post: Post):
    cursor.execute("UPDATE posts SET content = %s WHERE id = %s RETURNING * ",(post.content, id))
    updated_post = cursor.fetchone()
    connection.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id {id} not found!!')
    return {"data":updated_post}
