from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255))
    password = Column(String(255))
    phone_number = Column(String(255))
    role = Column(String(255))
    username = Column(String(255))

    requests = relationship("Request", back_populates="user")