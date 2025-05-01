from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # 'income' or 'expense'
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)  # Store color code
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Allow user-defined categories, default categories have no user ID
    is_default = Column(Boolean, default=False)  # Mark if it's a system default category
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="category")
    user = relationship("User")
    
    # Constraints
    __table_args__ = (UniqueConstraint('name', 'type', 'user_id', name='uix_category_name_type_user'),)