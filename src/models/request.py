from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class RequestLikes(Base):
    __tablename__ = 'requests_likes'

    id = Column(BigInteger, primary_key=True, index=True)
    request_id = Column(BigInteger, ForeignKey('requests.id'))
    user_id = Column(BigInteger, ForeignKey('users.id'))
    user = relationship("User", foreign_keys=[user_id])
    request = relationship("Request", foreign_keys=[request_id])


class RequestCategory(Base):
    __tablename__ = 'request_categories'

    id = Column(BigInteger, primary_key=True, index=True)
    request_id = Column(BigInteger, ForeignKey('requests.id'))
    category_id = Column(BigInteger, ForeignKey('categories.id'))

    request = relationship("Request", back_populates="request_categories")
    category = relationship("Category", back_populates="request_categories")


class Request(Base):
    __tablename__ = 'requests'

    id = Column(BigInteger, primary_key=True, index=True)
    description = Column(String)
    creation_time = Column(BigInteger)
    location = Column(String)
    user_id = Column(BigInteger, ForeignKey('users.id'))

    user = relationship("User", back_populates="requests")
    request_categories = relationship("RequestCategory", back_populates="request")

    def __init__(self, description, location, user):
        self.description = description
        self.location = location
        self.user = user

class Category(Base):
    __tablename__ = 'categories'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String)
    request_categories = relationship("RequestCategory", back_populates="category")
