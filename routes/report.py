#  routes/report.py
from models.shared_report import SharedReport
from models.shared_view import SharedView
from models.user import User  # if not already imported
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, Response
from flask_login import login_required, current_user
from models.transaction import Transaction
from sqlalchemy import and_
from dateutil import parser as date_parser
from db import get_db
from io import StringIO
import csv 

def build_filtered_query(db, user, params):
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    # If filtering by another owner (i.e., shared data)
    owner_id = params.get('owner_id')
    if owner_id and int(owner_id) != user.id:
        shared_report = db.query(SharedReport).filter_by(
            recipient_id=user.id,
            owner_id=owner_id
        ).order_by(SharedReport.created_at.desc()).first()

        if not shared_report:
            return db.query(Transaction).filter(False)  # Empty query

        query = db.query(Transaction).filter(Transaction.user_id == shared_report.owner_id)
        params = shared_report.filter_params  # override filters with shared ones

    from_date = params.get('from')
    to_date = params.get('to')
    category = params.get('category')
    txn_type = params.get('type')
    amount_filter = params.get('amount_filter')
    description_keyword = params.get('description')

    if from_date and to_date:
        try:
            start = date_parser.parse(from_date).date()
            end = date_parser.parse(to_date).date()
            query = query.filter(Transaction.date.between(start, end))
        except Exception:
            pass

    if category and category != '__all__':
        query = query.filter(Transaction.category == category)

    if txn_type and txn_type != '__all__':
        query = query.filter(Transaction.type == txn_type)

    if amount_filter:
        try:
            value = float(amount_filter)
            query = query.filter(Transaction.amount >= value)
        except Exception:
            pass

    if description_keyword:
        query = query.filter(Transaction.description.ilike(f"%{description_keyword}%"))

    return query

report_bp = Blueprint('report', __name__,url_prefix='/report')

@report_bp.route('/data', methods=['GET'])
@login_required
def report_data():
    db = get_db()
    params = request.args
    print("🔍 Incoming filter params:", params)
    query = build_filtered_query(db, current_user, params)
    results = query.order_by(Transaction.date).all()
    print(f"📦 Found {len(results)} transactions for user {current_user.email}")
    
    # ✅ Mark shared reports as viewed if data belongs to a shared owner
    owner_id = params.get('owner_id')
    if owner_id and owner_id.isdigit() and int(owner_id) != current_user.id:
        owner_id = int(owner_id)
        shared_reports = db.query(SharedReport).filter_by(
            owner_id=owner_id,
            recipient_id=current_user.id
        ).all()

        for sr in shared_reports:
            already_viewed = db.query(SharedView).filter_by(
                viewer_id=current_user.id,
                shared_report_id=sr.id
            ).first()
            if not already_viewed:
                db.add(SharedView(viewer_id=current_user.id, shared_report_id=sr.id))
        db.commit()

    return jsonify([{
        "date": t.date.isoformat(),
        "description": t.description,
        "amount": t.amount,
        "type": t.type,
        "category": t.category
    } for t in results])


@report_bp.route('/', methods=['GET'])
@login_required
def report():
    db = get_db()

    # Get available categories for the current user
    categories = [
        c[0] for c in db.query(Transaction.category).distinct().filter(Transaction.user_id == current_user.id)
    ]

    # Get dates for calendar highlighting
    transaction_dates = [
        t[0].isoformat()
        for t in db.query(Transaction.date)
                  .distinct()
                  .filter(Transaction.user_id == current_user.id)
    ]

    print(f"🗂 Categories for {current_user.email}: {categories}")
    print(f"📅 Transaction dates: {transaction_dates}")
    
    # All shares sent to the current user
    all_shared = db.query(SharedReport).options(joinedload(SharedReport.owner)).filter_by(recipient_id=current_user.id).all()

    # Find unviewed shares (for bell notification)
    viewed_ids = db.query(SharedView.shared_report_id).filter_by(viewer_id=current_user.id).all()
    unviewed_shares = [r for r in all_shared if (r.id,) not in viewed_ids]

    # Get distinct owners of shared reports
    shared_owner_ids = {r.owner_id for r in all_shared}
    shared_owners = db.query(User).filter(User.id.in_(shared_owner_ids)).all()

    return render_template(
        'main/report.html',
        active_page='report',
        categories=categories,
        transaction_dates=transaction_dates,
        new_shares=unviewed_shares,           # 👈 Needed for bell notification
        shared_owners=shared_owners,          # 👈 Needed for “Shared By” dropdown
        shared_notification=len(unviewed_shares) > 0
    )


@report_bp.route('/export', methods=['GET'])
@login_required
def export_csv():
    db = get_db()
    query = build_filtered_query(db, current_user, request.args)
    results = query.order_by(Transaction.date).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'Description', 'Amount', 'Type', 'Category'])
    for t in results:
        writer.writerow([t.date, t.description, t.amount, t.type, t.category])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=transactions.csv"}
    )

@report_bp.route('/share', methods=['POST'])
@login_required
def share_report():
    db = get_db()
    data = request.get_json()
    recipient_email = data.get("username")
    filters = data.get("filters")

    # Backend Guardrail
    query = build_filtered_query(db, current_user, filters)
    if query.filter(Transaction.user_id != current_user.id).first():
        return jsonify({"error": "Cannot share transactions that don't belong to you."}), 403

    # Lookup recipient
    try:
        recipient = db.query(User).filter_by(email=recipient_email).one()
    except NoResultFound:
        return jsonify({"error": "User with that email not found."}), 404

    # Save the shared report
    shared = SharedReport(
        owner_id=current_user.id,
        recipient_id=recipient.id,
        filter_params=filters,
        created_at=datetime.utcnow()
    )
    db.add(shared)
    db.commit()
    return jsonify({"status": "success", "message": f"Shared with {recipient.email}"})
