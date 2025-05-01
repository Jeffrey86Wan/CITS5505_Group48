from flask import Blueprint, render_template, g, request, flash, redirect, url_for
from db import get_db
from models import Category, Transaction
from auth import login_required
from datetime import datetime

# Create blueprint
bp = Blueprint('record', __name__, url_prefix='/record')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def index():
    db = get_db()
    
    # Get all expense and income categories
    expense_categories = db.query(Category).filter(Category.type == 'expense').all()
    income_categories = db.query(Category).filter(Category.type == 'income').all()
    
    # Handle form submission
    if request.method == 'POST':
        amount = request.form.get('amount')
        category_id = request.form.get('category_id')
        date = request.form.get('date')
        description = request.form.get('description')
        transaction_type = request.form.get('type', 'expense')
        
        error = None
        
        if not amount:
            error = 'Amount cannot be empty'
        elif not category_id:
            error = 'Category cannot be empty'
        elif not date:
            error = 'Date cannot be empty'
            
        if error is None:
            try:
                # Create new transaction record
                transaction = Transaction(
                    amount=float(amount),
                    type=transaction_type,
                    date=datetime.strptime(date, '%Y-%m-%d').date(),
                    category_id=category_id,
                    user_id=g.user.id,
                    description=description,
                    created_at=datetime.now()
                )
                
                db.add(transaction)
                db.commit()
                flash('Transaction recorded successfully!', 'success')
                return redirect(url_for('record.index'))
                
            except Exception as e:
                db.rollback()
                error = f'Recording failed: {str(e)}'
        
        flash(error, 'error')
    
    return render_template(
        'main/record.html', 
        active_page='record',
        expense_categories=expense_categories,
        income_categories=income_categories
    )