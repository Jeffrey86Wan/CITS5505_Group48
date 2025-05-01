# Import all models, this way you can import once to get all models
from models.user import User
from models.transaction import Transaction
from models.category import Category
from models.blog import Blog

# These models can be selectively exported
__all__ = ['User', 'Transaction', 'Category', 'Blog']