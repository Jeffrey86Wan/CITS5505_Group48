from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=True)  # Article summary
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category = Column(String(50), nullable=False)  # Blog category
    status = Column(String(20), default='published')  # 'draft', 'published', 'archived'
    cover_image = Column(String(255), nullable=True)  # Cover image URL
    view_count = Column(Integer, default=0)  # View count
    like_count = Column(Integer, default=0)  # Like count
    comment_count = Column(Integer, default=0)  # Comment count
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", back_populates="blogs")
    
    # Indexes
    __table_args__ = (
        Index('idx_blog_author', author_id),
        Index('idx_blog_created', created_at),
    )