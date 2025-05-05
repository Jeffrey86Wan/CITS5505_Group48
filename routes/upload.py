# /routes/upload.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os, json
from models import Upload, Transaction
from db import get_db
from services.pdf_service import extract_text_from_pdf
from services.chatgpt_service import send_to_chatgpt
from helpers.parse import parse_amount  # Assumes you have this
from helpers.prompt import build_prompt  # Assumes you have this
from dateutil import parser as date_parser

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

UPLOAD_FOLDER = 'uploads'
EXTRACTED_FOLDER = 'extracted_texts'
GPT_OUTPUT_FOLDER = 'gpt_outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)
os.makedirs(GPT_OUTPUT_FOLDER, exist_ok=True)

@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('pdf_file')
        if not file:
            flash("No file selected", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(pdf_path)

        extracted_text = extract_text_from_pdf(pdf_path)
        base_name = os.path.splitext(filename)[0]
        txt_path = os.path.join(EXTRACTED_FOLDER, f"{base_name}.txt")
        with open(txt_path, 'w') as f:
            f.write(extracted_text)

        prompt = build_prompt(extracted_text)
        gpt_response = send_to_chatgpt(prompt,user_id=current_user.id)
        unique_categories = sorted(list({item.get('category', 'Uncategorized') for item in gpt_response}))
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        gpt_filename = f"{base_name}_{timestamp}.json"
        gpt_path = os.path.join(GPT_OUTPUT_FOLDER, gpt_filename)
        with open(gpt_path, 'w') as f:
            json.dump(gpt_response, f, indent=2)

        return render_template('main/upload.html',
                               active_page='upload',
                               extracted_json=gpt_response,
                               gpt_filename=gpt_filename,
                               filename=filename,
                               categories=unique_categories)

    return render_template('main/upload.html', active_page='upload',categories=[])


@upload_bp.route('/edit-upload', methods=['POST'])
@login_required
def edit_upload():
    try:
        db = get_db()
        data = request.get_json()

        upload = Upload(
            filename=data.get('filename', 'manual_upload'),
            user_id=current_user.id,  # ✅ this is required
            created_at=datetime.utcnow()
        )
        db.add(upload)
        db.flush()
        
        new_items, duplicates = 0, 0
        new_tnx = data.get('new', [])

        for item in new_tnx:
            amount = parse_amount(item.get('amount'))
            if amount is None or not item.get('description'):
                continue
            try: #use try-except to handle possible GPT malformed dates
                # item.get checks if key exists and returns None if not
                # date_parser.parse(item['date'], dayfirst=True) will raise an exception if the date is invalid
                # We use dayfirst=True to handle European date formats
                parsed_date = date_parser.parse(item['date'], dayfirst=True).date() if item.get('date') else None
            except Exception:
                parsed_date = None

            existing_transaction = db.query(Transaction).filter_by(
                date=parsed_date,
                description=item['description'].strip(),
                amount=amount,
                type=item['type']
            ).first()

            if existing_transaction:
                duplicates += 1
                continue

            txn = Transaction(
                description=item['description'],
                amount=amount,
                category=item.get('category', 'Uncategorized'),
                date=parsed_date,
                type=item['type'],
                user_id=current_user.id,   # ✅ Fix for current error
                #upload_id=upload.id # here we use the upload ID from the upload object to associate the transaction
            )

            db.add(txn)
            new_items += 1

        db.commit()
        return jsonify({
            "status": "success",
            "message": f"Expenses saved successfully! {new_items} new items, {duplicates} duplicates skipped."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # g is an object and imported from flask
    # every web request creates a new g object and behaves like a global variable which is a python dictionary
    # g.db is a database session which is stored as db 
    # g = request-scoped storage to avoid global variables
    # get_db() = smart session getter for each request
    # flush() = sends changes to DB but allows rollback
    # commit() = final write to DB
    # Base = lets models map to tables
    # engine = the DB connector
    # SessionLocal = the factory that gives each request its own notepad (session)
    # scoped_session(...) makes it thread-safe, so that each user/request/thread gets its own session.