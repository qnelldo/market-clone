from fastapi import FastAPI, UploadFile, Form, Response, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3
import hashlib



con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()

app = FastAPI()

SECRET = "super-coding"
manager = LoginManager(SECRET, '/login.html')

# @manager.user_loader()
# def query_user(id):
#     con.row_factory = sqlite3.Row
#     cur = con.cursor()
#     user = cur.execute(f""" 
#                    SELECT * FROM users WHERE id=?
#                    """, (id,)).fetchone()
#     return user

@manager.user_loader()  
def query_user(data):
    WHERE_STATEMENTS = f'''id="{data}"'''
    if type(data) == dict:
          WHERE_STATEMENTS = f'''id="{data['id']}"'''
    con.row_factory = sqlite3.Row
    cur = con.cursor()  
    user = cur.execute(f"""
                       SELECT * FROM users WHERE {WHERE_STATEMENTS}
                       """).fetchone()
    return user





@app.post('/login')
def login(id:Annotated[str,Form()], 
          password:Annotated[str, Form()]):
    
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    
    user = query_user(id)
    if not user:
        raise InvalidCredentialsException
    elif hash_password != user['password']:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(data={
        'sub' : {
            'id' : user['id'],
            'name' : user['name'],
            'email' : user['email']
            }
        })
    return {'access_token':access_token}


@app.post('/signup')
def signup(id:Annotated[str,Form()], 
           password:Annotated[str, Form()],
           name:Annotated[str, Form()],
           email:Annotated[str, Form()]):
    
    hash_password = hashlib.sha256(password.encode()).hexdigest()
    
    cur.execute(f"""
                INSERT INTO users(id, name, email, password)
                VALUES ('{id}', '{name}', '{email}', '{hash_password}')
                """)
    
    con.commit()
    return '200'


@app.post('/items')
async def create_item(image:UploadFile, 
                title:Annotated[str,Form()], 
                price:Annotated[int,Form()], 
                description:Annotated[str,Form()], 
                place:Annotated[str,Form()],
                insertAt:Annotated[int, Form()],
                user=Depends(manager)
                ):
    
    image_bytes = await image.read()
    
    cur.execute(f"""
                INSERT INTO items(title, image, price, description, place, insertAt)
                VALUES ('{title}', '{image_bytes.hex()}','{price}','{description}', '{place}','{insertAt}')
                """)
    
    con.commit()
    return '200'
    
@app.get('/items')
async def get_items(user=Depends(manager)):
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute(f"""
                       SELECT * FROM items;
                       """).fetchall()
    
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))

@app.get('/images/{item_id}')
async def get_img(item_id):
    cur = con.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image FROM items WHERE id ={item_id}
                              """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')
    





app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")