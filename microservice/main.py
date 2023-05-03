import asyncio
import json
import logging

from fastapi import FastAPI

from database import Session, KAFKA_INSTANCE
from models import User, Post, Like, UserPage
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


logger = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
aioproducer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_INSTANCE)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    loop.create_task(consume())


@app.on_event("shutdown")
async def shutdown_event():
    await aioproducer.stop()

async def consume():
    await asyncio.sleep(15)
    consumer = AIOKafkaConsumer("req", bootstrap_servers=KAFKA_INSTANCE, loop=loop)
    logger.info("Created consumer")
    await consumer.start()
    try:
        async for msg in consumer:
            logger.info("Reading message")
            value = msg.value.decode("utf-8")
            id = int(value[8])

            # country = Session.query(Country).filter(Country.id == 1).first()
            # if not country:
            #     my_contry = Country(country_name="Japan")
            #     Session.add(my_contry)
            #     Session.commit()
            #     logger.info("Created Country successfully")
            #     Session.refresh()
            #     country = Session.query(Country).filter(Country.id == 1).first()
            logger.info("Created Country successfully and go next")
            posts_count = Session.query(Post).filter(Post.page_id == id).count()
            followers_count = Session.query(User).join(UserPage, User.id == UserPage.user_id).filter(
                UserPage.page_id == id).count()
            likes_count = Session.query(Like).join(Post, Like.post_to_id == Post.id).filter(Post.page_id == id).count()

            answer = {
                "id": id,
                "posts_count": posts_count,
                "followers_count": followers_count,
                "likes_count": likes_count,
                "country": 1,
            }

            await aioproducer.start()
            await aioproducer.send("res", json.dumps(answer).encode("utf-8"))
            logger.info("Message processed")
    except Exception as err:
        logger.exception(err)
    finally:
        await consumer.stop()
        print("Success")


# @app.get('/{id}')
# async def index(id: int):
#     # conn = psycopg2.connect(database=os.getenv("NAME"),
#     #                         host=os.getenv("HOST1"),
#     #                         user=os.getenv("USER2"),
#     #                         password=os.getenv("PASSWORD2"),
#     #                         port=os.getenv("PORT1"))
#     #
#     # cursor = conn.cursor()
#     #
#     # cursor.execute(f"SELECT COUNT(*) FROM facebookk_post WHERE page_id = {id}")
#     # posts_count = cursor.fetchall()
#     #
#     # cursor.execute(f"SELECT COUNT(*) FROM myuser_user INNER JOIN facebookk_page_followers ON "
#     #                f"myuser_user.id = facebookk_page_followers.user_id WHERE facebookk_page_followers.page_id = {id}")
#     # followers_count = cursor.fetchall()
#     #
#     # cursor.execute(f"SELECT COUNT(*) FROM facebookk_like WHERE facebookk_like.post_to_id IN( SELECT U0.id FROM facebookk_post U0 WHERE U0.page_id={id})")
#     # likes_count = cursor.fetchall()
#     # conn.close()
#     #
#     # posts_count = Session.query(Post).filter(Post.page_id==id).count()
#     # followers_count = Session.query(User).join(UserPage, User.id == UserPage.user_id).filter(UserPage.page_id == id).count()
#     # likes_count = Session.query(Like).join(Post, Like.post_to_id == Post.id).filter(Post.page_id == id).count()
#     #
#     #
#     # answer = {
#     #         "posts_count": posts_count,
#     #         "followers_count": followers_count,
#     #         "likes_count": likes_count,
#     #         }
#     #
#     #
#     # return answer
#     global consumer
#     try:
#         async for msg in consumer:
#             id = msg.value["id"]
#             posts_count = Session.query(Post).filter(Post.page_id == id).count()
#             followers_count = Session.query(User).join(UserPage, User.id == UserPage.user_id).filter(
#                 UserPage.page_id == id).count()
#             likes_count = Session.query(Like).join(Post, Like.post_to_id == Post.id).filter(Post.page_id == id).count()
#             answer = {
#                 "id": id,
#                 "posts_count": posts_count,
#                 "followers_count": followers_count,
#                 "likes_count": likes_count,
#             }
#             await aioproducer.start()
#             await aioproducer.send("res", json.dumps(answer).encode("utf-8"))
#             await aioproducer.stop()
#     finally:
#         print("end")
