import json
import os

from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from mysite import settings
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()


@app.get('/{id}')
async def index(id: int):
    conn = psycopg2.connect(database=os.getenv("NAME"),
                            host=os.getenv("HOST1"),
                            user=os.getenv("USER2"),
                            password=os.getenv("PASSWORD2"),
                            port=os.getenv("PORT1"))

    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM facebookk_post WHERE page_id = {id}")
    posts_count = cursor.fetchall()

    cursor.execute(f"SELECT COUNT(*) FROM myuser_user INNER JOIN facebookk_page_followers ON "
                   f"myuser_user.id = facebookk_page_followers.user_id WHERE facebookk_page_followers.page_id = {id}")
    followers_count = cursor.fetchall()

    cursor.execute(f"SELECT COUNT(*) FROM facebookk_like WHERE facebookk_like.post_to_id IN( SELECT U0.id FROM facebookk_post U0 WHERE U0.page_id={id})")
    likes_count = cursor.fetchall()
    conn.close()

    answer = {
            "posts_count": posts_count[0][0],
            "followers_count":followers_count[0][0],
            "likes_count": likes_count[0][0],
            }

    return answer
