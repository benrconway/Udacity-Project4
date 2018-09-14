from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)  # NOQA


Base = declarative_base()
key = ''.join(random.choice(string.ascii_uppercase +
              string.digits) for x in xrange(32))


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    password_hash = Column(String(250))

    def hashPassword(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verifyPassword(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generateToken(self, expiration=600):
        s = Serializer(key, expires_in=expiration)
        return s.dumps({'id': self.id})


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)
    # if a category is deleted, then all their items should also be deleted.
    item = relationship("Items", cascade="all,delete, delete-orphan",
                        backref="Categories")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id
        }


class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    location = Column(String(250))
    url = Column(String(250))
    category_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)
    category = relationship(Categories)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'url': self.url,
            'user_id': self.user_id,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///itemcatalogue.db')

Base.metadata.create_all(engine)
