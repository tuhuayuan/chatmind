# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'users'
    __table_arg__ = {
        "mysql_engine": "MyISAM",
    }

    id = Column(Integer, primary_key=True)
    openid = Column(String(128), nullable=False, index=True)
    platform = Column(Integer, nullable=False)
    name = Column(String(128), nullable=True)


class Token(BaseModel):
    __tablename__ = 'tokens'
    __table_arg__ = {
        "mysql_engine": "MyISAM"
    }

    tokenid = Column(String(512), primary_key=True)
    expired = Column(Integer, default=0)

def init_db(engine):
    BaseModel.metadata.create_all(engine)


def drop_db(engine):
    BaseModel.metadata.drop_all(engine)
