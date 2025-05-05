from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(50), default="pending")  # e.g., 'pending', 'processed', 'error'
    gpt_output_path = Column(String(255), nullable=True)  # Path to GPT output JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="uploads")
