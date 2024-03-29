from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table
from database import Base, metadata, engine

association_table = Table(
    "facebookk_page_followers",
    metadata,
    Column("user_id", ForeignKey("myuser_user.id"), primary_key=True),
    Column("page_id", ForeignKey("facebookk_page.id"), primary_key=True),
)

class UserPage(Base):
    __tablename__ = Table("facebookk_page_followers", metadata, autoloa=True, autoload_with=engine)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("myuser_user.id"))
    page_id = Column(Integer, ForeignKey("facebookk_page.id"))

class User(Base):
    __tablename__ = Table("myuser_user", metadata, autoload_replace=True, autoload_with=engine)
    id = Column(Integer, primary_key=True)
    username = Column(String)

class Page(Base):
    __tablename__ = Table("facebookk_page", metadata, autoload_replace=True, autoload_with=engine)
    id = Column(Integer, primary_key=True)
    # followers = relationship("User", secondary=UserPage.__tablename__,
    #                          #foreign_keys=[association_table.c.user_id, association_table.c.page_id],
    #                          #primaryjoin=(association_table.c.page_id == "facebookk_page.id"),
    #                          #secondaryjoin=(association_table.c.user_id == "myuser_user.id"),
    #                          )

class Post(Base):
    __tablename__ = Table("facebookk_post", metadata, autoload_replace=True, autoload_with=engine)
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer)

class Like(Base):
    __tablename__ = Table("facebookk_like", metadata, autoload_replace=True, autoload_with=engine)
    id = Column(Integer, primary_key=True)
    post_to_id = Column(Integer)
    user_from_id = Column(Integer)

# class Country(Base):
#     __tablename__ = "country"
#     id = Column(Integer, primary_key=True)
#     country_name = Column(String(50), unique=True, nullable=False)
#     people = relationship("Human", back_populates="country")
# class Human(Base):
#     __tablename__ = "human"
#     id = Column(Integer, primary_key=True)
#     human_name = Column(String(50), unique=True, nullable=False)
#     birth_year = Column(Integer, nullable=False)
#     country_id = Column(Integer, ForeignKey("country.id"))
#     country = relationship("Country", back_populates="people")

