from src.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_NAME,
    DB_PASSWORD
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    sessions = relationship("Session", backref="user")


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_id = Column(Integer, ForeignKey('games.id'))


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    sessions = relationship("Session", backref="game")
