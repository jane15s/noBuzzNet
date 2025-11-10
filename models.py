from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    hashed_password = Column(String(255))
    email = Column(String(120), unique=True, nullable=False)
    auth_provider = Column(String(20), default="local")

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r} email={self.email!r} auth_provider={self.auth_provider}>"


class Link(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    link = Column(String(255), nullable=False)
    description = Column(String(100))
    datetime_created =Column(DateTime(timezone=True), server_default=func.now())
    owner = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    icon = Column(String(255))

    def __repr__(self):
        return (f"<Link id={self.id} description={self.description!r} "
                f"datetime_created={self.datetime_created} owner={self.owner} icon={self.icon}>")