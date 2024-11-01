from flask import Blueprint, jsonify, request
from app.models.user import Users
from app.models.account import Accounts
from app.models.transactions import Transactions
from app.connectors.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager # type: ignore

user_blueprint = Blueprint("user_blueprint", __name__)
jwt = JWTManager()

@user_blueprint.route("/", methods=["GET"])
def get_users():
    users = Users.query.all()
    return jsonify([user.as_dict() for user in users]),200

def hash_password(password):
    """Hash password using Werkzeug."""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def verify_password(password, hashed_password):
    """Verify password against hashed password."""
    return check_password_hash(hashed_password, password)

@user_blueprint.route("/register", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.get_json()
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Invalid input"}), 400

    # Hash the password
    hashed_password = hash_password(data['password'])
    
    # Create a new user instance
    new_user = Users(
        username=data["username"],
        email=data["email"],
        password_hash=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify(new_user.as_dict()), 201

@user_blueprint.route("/profile/<user_id>", methods=["GET"])
@jwt_required()
def get_profile(user_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.id != identity:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(user.as_dict()), 200

@user_blueprint.route("/profile/<user_id>", methods=["PUT"])
@jwt_required()
def update_profile(user_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=user_id).first()

    # Cek apakah user ada
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Cek apakah user yang mengakses adalah pemilik akun
    if user.id != identity:
        return jsonify({"error": "Unauthorized"}), 401

    # Ambil data dari request JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update data user yang diizinkan
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)

    # Simpan perubahan ke database
    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully", "user": user.as_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500

@user_blueprint.route("/login", methods=["POST"])
def login():
    """Authenticate and log in a user, returning a JWT token."""
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Invalid input"}), 400

    user = Users.query.filter_by(email=data["email"]).first()
    if not user or not verify_password(data["password"], user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

# @user_blueprint.route("/me", methods=["PUT"])
# @jwt_required()
# def update_current_user():
#     """Update the profile information of the currently authenticated user."""
#     current_user_id = get_jwt_identity()
#     user = Users.query.get(current_user_id)

#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     data = request.get_json()

#     # Update only the fields that are provided in the request
#     if "username" in data:
#         user.username = data["username"]
#     if "email" in data:
#         user.email = data["email"]
#     if "password" in data:
#         user.password_hash = hash_password(data["password"])

#     user.updated_at = datetime.utcnow()

#     try:
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

#     return jsonify(user.as_dict()), 200
