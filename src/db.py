from src.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_NAME,
    DB_PASSWORD
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

Engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
DBSession = sessionmaker(bind=Engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    session = relationship("Session", uselist=False, backref="user")


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_id = Column(Integer, ForeignKey('games.id'))


class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    sessions = relationship("Session", backref="game")
    rounds = relationship("Round", backref="game")


class Round(Base):
    __tablename__ = 'rounds'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    phase = Column(String, default='set_up')
    completed = Column(Boolean, default=False)
    set_up_phase = relationship("SetUpPhase", uselist=False, backref="round")
    clue_phase = relationship("CluePhase", uselist=False, backref="round")
    vote_phase = relationship("VotePhase", uselist=False, backref="round")
    reveal_phase = relationship("RevealPhase", uselist=False, backref="round")


class SetUpPhase(Base):
    __tablename__ = 'setup_phases'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    chameleon_session_id = Column(Integer)  # not using a FKey to avoid linking tables and for on_delete simplicity
    category = Column(String)
    big_die_roll = Column(Integer)
    small_die_roll = Column(Integer)


class CluePhase(Base):
    __tablename__ = 'clue_phases'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    clues = Column(JSON)


class VotePhase(Base):
    __tablename__ = 'vote_phases'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    votes = Column(JSON)


class RevealPhase(Base):
    __tablename__ = 'reveal_phases'

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    guess = Column(String)
