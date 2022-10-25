
from fastapi import FastAPI

from microservice.database import Session
from microservice.models import User, Page, Post, Like, UserPage
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)


app = FastAPI()


@app.get('/{id}')
async def index(id: int):
    # conn = psycopg2.connect(database=os.getenv("NAME"),
    #                         host=os.getenv("HOST1"),
    #                         user=os.getenv("USER2"),
    #                         password=os.getenv("PASSWORD2"),
    #                         port=os.getenv("PORT1"))
    #
    # cursor = conn.cursor()
    #
    # cursor.execute(f"SELECT COUNT(*) FROM facebookk_post WHERE page_id = {id}")
    # posts_count = cursor.fetchall()
    #
    # cursor.execute(f"SELECT COUNT(*) FROM myuser_user INNER JOIN facebookk_page_followers ON "
    #                f"myuser_user.id = facebookk_page_followers.user_id WHERE facebookk_page_followers.page_id = {id}")
    # followers_count = cursor.fetchall()
    #
    # cursor.execute(f"SELECT COUNT(*) FROM facebookk_like WHERE facebookk_like.post_to_id IN( SELECT U0.id FROM facebookk_post U0 WHERE U0.page_id={id})")
    # likes_count = cursor.fetchall()
    # conn.close()

    posts_count = Session.query(Post).filter(Post.page_id==id).count()
    followers_count = Session.query(User).join(UserPage, User.id == UserPage.user_id).filter(UserPage.page_id == id).count()
    likes_count = Session.query(Like).join(Post, Like.post_to_id == Post.id).filter(Post.page_id == id).count()


    answer = {
            "posts_count": posts_count,
            "followers_count": followers_count,
            "likes_count": likes_count,
            }


    return answer