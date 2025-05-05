# models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base
from flask_login import UserMixin

class User(Base,UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    oauth_provider = Column(String(50), nullable=True)  # e.g., 'google'
    oauth_id = Column(String(255), nullable=True)       # e.g., Google user ID
    created_at = Column(DateTime, default=datetime.utcnow)
    avatar = Column(String(255), nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    uploads = relationship("Upload", back_populates="user")

    # blogs = relationship("Blog", back_populates="author")