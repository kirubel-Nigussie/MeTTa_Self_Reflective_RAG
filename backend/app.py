import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.orchestrator import run_pipeline
from services.pdf_loader import save_pdf, pdf_to_chunks
from services.vector_store import add_chunks
from services.auth import register_user, authenticate_user, token_required, generate_token, get_user_by_id
from models import db, User
from config import settings

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Authentication endpoints
@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data required"}), 400
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    user_id, message = register_user(username, email, password)
    
    if user_id:
        token = generate_token(user_id)
        user_data = get_user_by_id(user_id)
        return jsonify({
            "status": "success",
            "message": message,
            "token": token,
            "user": user_data
        }), 201
    else:
        return jsonify({
            "status": "error",
            "message": message
        }), 400

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data required"}), 400
    
    username_or_email = data.get("username", "").strip()
    password = data.get("password", "")
    
    user_id, message = authenticate_user(username_or_email, password)
    
    if user_id:
        token = generate_token(user_id)
        user_data = get_user_by_id(user_id)
        return jsonify({
            "status": "success",
            "message": message,
            "token": token,
            "user": user_data
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": message
        }), 401

@app.route("/auth/profile", methods=["GET"])
@token_required
def get_profile(current_user_id):
    user_data = get_user_by_id(current_user_id)
    return jsonify({
        "status": "success",
        "user": user_data
    }), 200

@app.route("/upload_pdf", methods=["POST"])
@token_required
def upload_pdf(current_user_id):
    if "file" not in request.files:
        return jsonify({"error": "file required (multipart form field 'file')"}), 400
    f = request.files["file"]
    path = save_pdf(f)
    
    # Use LangChain-based chunking (proven to work)
    chunks = pdf_to_chunks(path)
    add_chunks(chunks, batch_size=settings.EMBED_BATCH_SIZE)
    
    return jsonify({"status":"ok","ingested": len(chunks),"source": os.path.basename(path)})

@app.route("/ask", methods=["POST"])
@token_required
def ask(current_user_id):
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error":"query required"}), 400
    query = data["query"]
    top_k = data.get("top_k")
    res = run_pipeline(query, top_k=top_k)
    return jsonify(res)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
