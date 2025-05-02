import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance
from pdf2image import convert_from_path

app = Flask(__name__)
app.secret_key = '2a8b84c9e1a748cc97394896e1124a1b6a7b88b2341cd8337d2ea110ee6c2a34'
UPLOAD_FOLDER = 'static/uploads'
THUMBNAIL_FOLDER = 'static/thumbnails'
DATA_FILE = 'static/data/documents.json'

ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'odt', 'ods', 'odp', 'jpg', 'jpeg', 'png'
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #bytes

for folder in [UPLOAD_FOLDER, THUMBNAIL_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(file_path, filename, file_ext):
    thumbnail_filename = f"{filename.rsplit('.', 1)[0]}_thumb.png"
    thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
    default_thumbnail = 'static/images/default-thumbnail.png'

    try:
        if file_ext == 'pdf':
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=200)
            img = images[0]
            img.thumbnail((300, 300))
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            img.save(thumbnail_path, 'PNG', quality=95)
        elif file_ext in ['jpg', 'jpeg', 'png']:
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            img.save(thumbnail_path, 'PNG', quality=95)
        else:
            # File không phải PDF/jpg/png, trả về default
            return default_thumbnail
    except Exception as e:
        print(f"Error creating thumbnail for {filename}: {e}")
        return default_thumbnail

    return thumbnail_path.replace('\\', '/') if os.path.exists(thumbnail_path) else default_thumbnail


def count_pages(file_path, file_ext):
    if file_ext != 'pdf':
        return None
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    try:
        images = convert_from_path(file_path, dpi=72)
        return len(images)
    except Exception as e:
        print(f"Error counting pages for {file_path}: {e}")
        return None

@app.errorhandler(RequestEntityTooLarge)
def too_large(error):
    flash ("Tập tin quá lớn (tối đa 16MB). Vui lòng chọn lại.","error"),
    return redirect(request.url)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.route('/')
def home():
    with open('static/data/document_types.json', 'r', encoding='utf-8') as f:
        document_types = json.load(f)['document_types']
    return render_template('home.html', document_types=document_types)


@app.route('/all-documents')
def all_documents():
    with open('static/data/documents.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify({"documents": data['documents']})


@app.route('/documents')
def documents():
    # Lấy tham số
    query = request.args.get('q', '').lower()
    category_filter = request.args.get('category', 'all')
    doc_type_filter = request.args.get('doc_type', 'all')
    page = int(request.args.get('page', 1))
    per_page = 20

    # Load dữ liệu
    with open('static/data/documents.json', 'r', encoding='utf-8') as f:
        all_docs = json.load(f).get('documents', [])
    with open('static/data/categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f).get('categories', [])
    with open('static/data/document_types.json', 'r', encoding='utf-8') as f:
        document_types = json.load(f).get('document_types', [])

    # 1) Lọc theo từ khóa
    docs = all_docs
    if query:
        docs = [d for d in docs if query in d.get('title', '').lower()]

    # 2) Lọc theo loại tài liệu
    if doc_type_filter != 'all':
        docs = [d for d in docs if str(d.get('document_type')) == str(doc_type_filter)]

    # 3) Nếu chọn 1 khoa cụ thể, chỉ giữ lại docs của khoa đó
    if category_filter != 'all':
        docs = [d for d in docs if str(d.get('category')) == str(category_filter)]
        docs_flat = docs
    else:
        # 4) Gom docs theo khoa
        docs_by_cat = {}
        for cat in categories:
            cat_id = str(cat['id'])
            docs_by_cat[cat_id] = [d for d in docs if str(d.get('category')) == cat_id]
        # 5) “Phẳng hoá” theo thứ tự khoa
        docs_flat = []
        for cat in categories:
            docs_flat.extend(docs_by_cat.get(str(cat['id']), []))

    # 6) Tính tổng và phân trang
    total_docs = len(docs_flat)
    total_pages = (total_docs + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    docs_paginated = docs_flat[start:end]

    # 7) Gom lại theo khoa cho template
    categorized_docs = {}
    for d in docs_paginated:
        cid = str(d.get('category'))
        categorized_docs.setdefault(cid, []).append(d)

    # Debug thumbnail
    print(f"Category Filter: {category_filter}")
    for doc in docs_paginated:
        print(f"Document ID: {doc['id']}, Category: {doc.get('category')}, Thumbnail: {doc.get('thumbnail', 'Không có')}, File: {doc.get('file')}")

    return render_template('document_list.html',
                           categorized_docs=categorized_docs,
                           categories=categories,
                           document_types=document_types,
                           query=query,
                           category_filter=category_filter,
                           doc_type_filter=doc_type_filter,
                           page=page,
                           total_pages=total_pages)

@app.route('/documents/<int:document_id>')
def view_document(document_id):
    with open('static/data/documents.json', 'r', encoding='utf-8') as file:
        documents_data = json.load(file)
    with open('static/data/categories.json', 'r', encoding='utf-8') as file:
        categories_data = json.load(file)
    with open('static/data/document_types.json', 'r', encoding='utf-8') as file:
        document_types_data = json.load(file)
    document = next((doc for doc in documents_data['documents'] if doc['id'] == document_id), None)
    if document is None:
        abort(404)

    # Chuẩn hóa file_path
    file_path = document['file_path'].replace('\\', '/')
    file_ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''

    # Đếm số trang
    page_count = count_pages(file_path, file_ext)
    if page_count is None:
        page_count = document.get('page_count') or 'Không áp dụng' if file_ext != 'pdf' else 'Không xác định'


    return render_template('view_document.html',
                           document=document,
                           categories=categories_data['categories'],
                           document_types=document_types_data['document_types'],
                           page_count=page_count)


@app.route('/upload', methods=['GET', 'POST'])
def upload_document():
    with open('static/data/categories.json', 'r', encoding='utf-8') as file:
        categories_data = json.load(file)
    with open('static/data/document_types.json', 'r', encoding='utf-8') as f:
        document_types_data = json.load(f)
    categories = categories_data['categories']
    document_types = document_types_data['document_types']
    if request.method == 'POST':
        title = request.form['title']
        category = str(request.form['category'])
        document_type = str(request.form['document_type'])
        lecturer = request.form.get('lecturer', '').strip()
        page_count = request.form.get('page_count', '')
        publish_year = request.form.get('publish_year', '')
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            thumbnail_path = create_thumbnail(file_path, filename, file_ext)
            calculated_page_count = count_pages(file_path, file_ext)
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    document_data = json.load(f)
            else:
                document_data = {'documents': []}
            documents = document_data['documents']
            new_id = documents[-1]['id'] + 1 if documents else 1
            new_doc = {
                'id': new_id,
                'title': title,
                'category': category,
                'document_type': document_type,
                'lecturer': lecturer if lecturer else None,
                'page_count': calculated_page_count if calculated_page_count else (
                    int(page_count) if page_count else None),
                'publish_year': int(publish_year) if publish_year else None,
                'file_path': os.path.join('static/uploads', filename).replace('\\', '/'),
                'thumbnail': thumbnail_path
            }
            documents.append(new_doc)
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, ensure_ascii=False, indent=4)
            flash('Tài liệu đã được tải lên thành công!')
            return redirect(url_for('upload_document'))
        else:
            flash('File không hợp lệ hoặc thiếu file!')
    return render_template('upload.html', categories=categories, document_types=document_types)


@app.route('/download/<filename>')
def download_document(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        flash('File không tồn tại!', 'error')
        return redirect(url_for('documents'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)