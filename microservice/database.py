import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

NAME = os.getenv("NAME")
USER = os.getenv("USER2")
PASSWORD = os.getenv("PASSWORD2")
HOST = os.getenv("HOST1")
PORT = os.getenv("PORT1")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Session = SessionLocal()
Base = declarative_base()
metadata = MetaData(bind=engine)


