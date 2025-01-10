from fastapi import FastAPI, HTTPException, Path, Query, Body
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import session

from models import Base, User, Post
from schemas import UserCreate, PostCreate, PostResponse
from database import engine, session_local


app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


users = [
    {'id': 1, 'name': 'John', 'age': 34},
    {'id': 2, 'name': 'Alex', 'age': 55},
    {'id': 3, 'name': 'Steve', 'age': 13},
]

posts = [
    {'id': 1, 'title': 'News 1', 'body': 'Text 1', 'author': users[0]},
    {'id': 2, 'title': 'News 2', 'body': 'Text 2', 'author': users[1]},
    {'id': 3, 'title': 'News 3', 'body': 'Text 3', 'author': users[2]},
]


@app.get('/items')
async def items() -> List[Post]:
    return [Post(**post) for post in posts]


@app.post('/items/add')
async def add_item(post: PostCreate) -> Post:
    author = next((user for user in users if user['id'] == post.author_id), None)
    if not author:
        raise HTTPException(status_code=404, detail='User not found')

    new_post_id = len(posts) + 1

    new_post = {'id': new_post_id, 'title': post.title, 'body': post.body, 'author': author}
    posts.append(new_post)

    return Post(**new_post)


@app.post('/user/add')
async def user_add(user: Annotated[
    UserCreate,
    Body(..., example={
        'name': 'UserName',
        'age': 1
    })
]) -> User:
    new_user_id = len(users) + 1

    new_user = {'id': new_user_id, 'name': user.name, 'age': user.age}
    posts.append(new_user)

    return Post(**new_user)


@app.get('/items/{item_id}')
async def item(item_id: Annotated[int, Path(..., title='Здесь указывается id поста', ge=1, lt=100)]) -> Post:
    for post in posts:
        if post['id'] == item_id:
            return Post(**post)

    raise HTTPException(status_code=404, detail='Post not found')


@app.get('/search')
async def search(post_id: Annotated[
    Optional[int],
    Query(title='ID of post to search for', ge=1, le=50),  # Работает с теми параметрами, что передаются после ?, &
]) -> Dict[str, Optional[Post]]:
    if post_id:
        for post in posts:
            if post['id'] == post_id:
                return {'data': Post(**post)}
        raise HTTPException(status_code=404, detail='Post not found')
    else:
        return {'data': None}
