# models/transaction.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(20), nullable=False)             # 'debit' or 'credit'
    category = Column(String(50), nullable=True)          # Category name (e.g. 'Groceries', 'Rent')
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #upload_id = Column(Integer, ForeignKey('uploads.id'))

    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'date'),
        Index('idx_transaction_category', 'category'),  # Now indexes the string field
    )
