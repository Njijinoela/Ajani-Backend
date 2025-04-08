from flask import Blueprint, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
from Models import db,Article
from PyPDF2 import PdfReader
from docx import Document

article_bp = Blueprint("articles", __name__)

@article_bp.route("/articles", methods=["POST"])
def create_article():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads/', filename) 
        file.save(file_path)

    data = request.form  
    article = Article(
        title=data.get("title"),
        content=data.get("content"),
        author=data.get("author"),
        file_path=file_path  
    )
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify({"message": "Article created", "id": article.id}), 201
@article_bp.route("/articles", methods=["GET"])
def get_articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "content": a.content,
        "author": a.author,
        "created_at": a.created_at
    } for a in articles])

@article_bp.route("/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
    article = Article.query.get_or_404(article_id)
    file_text = ""

    if article.file_path:
        file_ext = os.path.splitext(article.file_path)[1].lower()
        full_path = os.path.join(os.getcwd(), article.file_path)

        try:
            if file_ext == ".pdf":
                with open(full_path, 'rb') as f:
                    reader = PdfReader(f)
                    file_text = "\n".join(page.extract_text() or "" for page in reader.pages)

            elif file_ext == ".docx":
                doc = Document(full_path)
                file_text = "\n".join([para.text for para in doc.paragraphs])

        except Exception as e:
            print("File read error:", str(e))
            file_text = "[Error reading file content]"

    return jsonify({
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "created_at": article.created_at,
        "content": article.content,
        "file_text": file_text
    })

@article_bp.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)

@article_bp.route("/articles/<int:article_id>/file", methods=["GET"])
def get_article_file(article_id):
    article = Article.query.get_or_404(article_id)

    if not article.file_path:
        return jsonify({"error": "No file associated"}), 404

    file_directory = os.path.join(os.getcwd(), 'uploads')
    file_name = os.path.basename(article.file_path)

    try:
        return send_from_directory(file_directory, file_name)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@article_bp.route("/articles/<int:article_id>", methods=["PUT"])
def update_article(article_id):
    article = Article.query.get_or_404(article_id)
    data = request.json
    article.title = data.get("title", article.title)
    article.content = data.get("content", article.content)
    article.author = data.get("author", article.author)
    db.session.commit()
    return jsonify({"message": "Article updated"})

@article_bp.route("/articles/<int:article_id>", methods=["DELETE"])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({"message": "Article deleted"})
