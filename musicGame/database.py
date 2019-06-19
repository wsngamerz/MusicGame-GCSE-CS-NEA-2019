#
# musicGame/database.py
# by William Neild
#

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


db_engine = create_engine("sqlite:///main.db")

session_factory = sessionmaker(bind=db_engine)
Session = scoped_session(session_factory)
db_session = Session()

Base = declarative_base(bind=db_engine)


class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True)
    first_name = Column("first_name", String)
    last_name = Column("last_name", String)
    username = Column("username", String, unique=True)
    password = Column("password", String)

    results = relationship("Result", backref="user")


class Result(Base):
    __tablename__ = "results"
    id = Column("id", Integer, primary_key=True)
    user_id = Column("user", Integer, ForeignKey("users.id"))
    questions_correct = Column("correct", Integer)
    questions_incorrect = Column("incorrect", Integer)
    score = Column("score", Integer)

# TODO:
# Create a songs and playlists database table so that the songs and
# playlists can be stored so that we are not constantly querieing the
# spotify api for data which will cause lots of extra time starting
# up the application that shouldn't be needed.
# ALSO: possibly store audio as a binary blob in the db to prevent
# files cluttering and make it easier to delete when theyre no longer
# in the playlist

# NOTE: Not enough time to implement this

class Song(Base):
    __tablename__ = "songs"
    id = Column("id", String, primary_key=True)
    name = Column("name", String)
    artists = Column("artists", String)
    location = Column("location", String)
    url = Column("url", String)
    playlist_id = Column("playlist", String, ForeignKey("playlists.id"))


class Playlist(Base):
    __tablename__ = "playlists"
    id = Column("id", String, primary_key=True)
    last_updated = Column("last_updated", Date)

    songs = relationship("Song", backref="playlist")


# Create databases and tables if not already exist
Base.metadata.create_all()
