# -*- coding: UTF-8 -*-
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'users'
    __table_args__ = {
        "mysql_engine": "MyISAM",
    }

    id = Column(Integer, primary_key=True)
    openid = Column(String(128), nullable=False, index=True)
    platform = Column(Integer, nullable=False)
    name = Column(String(128), nullable=True)


class Token(BaseModel):
    __tablename__ = 'tokens'
    __table_args__ = {
        "mysql_engine": "MyISAM"
    }

    id = Column(Integer, primary_key=True)
    tokenid = Column(Text(512), default='')
    expired = Column(Integer, default=0)

    @classmethod
    def get_current_token(cls, session):
        token = session.query(Token).order_by("id desc").first()
        if token is None:
            token = Token(tokenid='', expired=0)
            session.add(token)
            session.commit()
        return token
