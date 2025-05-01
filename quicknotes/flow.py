from flask import Blueprint, render_template, g, request, jsonify
from db import get_db
from models import Transaction, Category
from auth import login_required
from datetime import datetime, date
from sqlalchemy import and_
import math

# Create blueprint
bp = Blueprint('flow', __name__, url_prefix='/flow')

@bp.route('/', methods=('GET',))
@login_required
def index():
    db = get_db()
    
    # Get current page number, default is page 1
    page = request.args.get('page', 1, type=int)
    
    # Number of records per page, can be modified here
    per_page = 5
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    
    # Build query conditions
    query_conditions = [Transaction.user_id == g.user.id]
    
    # Add date filter conditions
    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query_conditions.append(and_(Transaction.date >= start_date_obj, Transaction.date <= end_date_obj))
    
    # Add transaction type filter conditions
    if transaction_type in ['income', 'expense']:
        query_conditions.append(Transaction.type == transaction_type)
    
    # Query total record count
    total_count = db.query(Transaction).filter(*query_conditions).count()
    
    # Calculate total pages
    total_pages = math.ceil(total_count / per_page) if total_count > 0 else 1
    
    # Adjust page number to ensure it's within valid range
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages
    
    # Query transactions for current page
    transactions = db.query(Transaction).filter(
        *query_conditions
    ).order_by(
        Transaction.date.desc()
    ).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    
    # Preload related category data
    for transaction in transactions:
        # Ensure category data is loaded
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
        transaction.category = category
    
    return render_template(
        'main/flow.html',
        active_page='flow',
        transactions=transactions,
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages
    )

@bp.route('/<int:transaction_id>/data', methods=('GET',))
@login_required
def get_transaction_data(transaction_id):
    """Get detailed data for a single transaction, used for edit form"""
    db = get_db()
    
    # Query transaction record
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == g.user.id  # Ensure user can only access their own records
    ).first()
    
    if not transaction:
        return jsonify({'success': False, 'message': 'Record does not exist or no permission to access'}), 404
    
    # Convert to JSON format
    transaction_data = {
        'id': transaction.id,
        'amount': float(transaction.amount),
        'type': transaction.type,
        'date': transaction.date.strftime('%Y-%m-%d'),
        'category_id': transaction.category_id,
        'description': transaction.description
    }
    
    return jsonify(transaction_data)

@bp.route('/categories/<string:type>', methods=('GET',))
@login_required
def get_categories(type):
    """Get list of categories for specified type"""
    if type not in ['income', 'expense']:
        return jsonify([])
    
    db = get_db()
    
    # Query system default categories and user custom categories
    categories = db.query(Category).filter(
        Category.type == type,
        (Category.is_default == True) | (Category.user_id == g.user.id)
    ).all()
    
    # Convert to JSON format
    categories_data = [
        {
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'color': category.color
        }
        for category in categories
    ]
    
    return jsonify(categories_data)

@bp.route('/<int:transaction_id>/edit', methods=('POST',))
@login_required
def edit_transaction(transaction_id):
    """Update transaction record"""
    db = get_db()
    
    # Query transaction to edit
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == g.user.id  # Ensure user can only edit their own records
    ).first()
    
    if not transaction:
        return jsonify({'success': False, 'message': 'Record does not exist or no permission to edit'}), 404
    
    try:
        # Get form data
        amount = request.form.get('amount')
        category_id = request.form.get('category_id')
        date = request.form.get('date')
        description = request.form.get('description', '')
        transaction_type = request.form.get('type')
        
        # Validate data
        if not amount or not category_id or not date or not transaction_type:
            return jsonify({'success': False, 'message': 'Please fill in all required fields'}), 400
        
        if transaction_type not in ['income', 'expense']:
            return jsonify({'success': False, 'message': 'Invalid transaction type'}), 400
            
        # Verify category exists and type matches
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.type == transaction_type,
            (Category.is_default == True) | (Category.user_id == g.user.id)
        ).first()
        
        if not category:
            return jsonify({'success': False, 'message': 'Category does not exist or type does not match'}), 400
        
        # Update transaction record
        transaction.amount = float(amount)
        transaction.type = transaction_type
        transaction.date = datetime.strptime(date, '%Y-%m-%d').date()
        transaction.category_id = category_id
        transaction.description = description
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Update successful'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500

@bp.route('/<int:transaction_id>/delete', methods=('POST',))
@login_required
def delete_transaction(transaction_id):
    """Delete transaction record"""
    db = get_db()
    
    # Query transaction to delete
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == g.user.id  # Ensure user can only delete their own records
    ).first()
    
    if not transaction:
        return jsonify({'success': False, 'message': 'Record does not exist or no permission to delete'}), 404
    
    try:
        # Delete transaction record
        db.delete(transaction)
        db.commit()
        
        return jsonify({'success': True, 'message': 'Delete successful'})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'message': f'Delete failed: {str(e)}'}), 500
