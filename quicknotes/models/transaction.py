from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Numeric, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)  # Amount, using Numeric to keep 2 decimal places
    type = Column(String(20), nullable=False)  # 'income' or 'expense'
    date = Column(Date, nullable=False)  # Transaction date
    time = Column(Time, nullable=True)  # Transaction time, optional
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(String(255), nullable=True)  # Detailed description
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_transaction_user_date', user_id, date),
        Index('idx_transaction_category', category_id),
    )