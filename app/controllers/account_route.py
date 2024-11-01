from email import message
import random
from flask import Blueprint, jsonify, request
from app.models.user import Users
from app.models.account import Accounts
from app.models.transactions import Transactions
from app.connectors.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager # type: ignore

account_blueprint = Blueprint("account_blueprint", __name__)
jwt = JWTManager()

@account_blueprint.route("/", methods=["GET"])
def get_accounts():
    accounts = Accounts.query.all()
    return jsonify({"massage": "success"}),200

def generate_unique_account_number():
    while True:
        account_number = random.randint(1000000, 9999999)  # Generate angka acak 7 digit
        existing_account = Accounts.query.filter_by(account_number=account_number).first()
        if not existing_account:
            return account_number  # Kembalikan jika account_number belum ada di database

@account_blueprint.route("/create_account", methods=["POST"])
@jwt_required()
def create_account():
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data or "account_type" not in data:
        return jsonify({"error": "Invalid input"}), 400

    # Generate account_number unik
    unique_account_number = generate_unique_account_number()

    new_account = Accounts(
        user_id=user.id,
        account_type=data["account_type"],
        account_number=unique_account_number,
        balance=0.0
    )
    
    try:
        db.session.add(new_account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Account created successfully",
        "account_number": unique_account_number
    }), 201
    
@account_blueprint.route("/get_accounts", methods=["GET"])
@jwt_required()
def get_account():
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    accounts = Accounts.query.filter_by(user_id=user.id).all()
    return jsonify([account.as_dict() for account in accounts]), 200

@account_blueprint.route("/get_account/<account_id>", methods=["GET"])
@jwt_required()
def get_account_by_id(account_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    account = Accounts.query.filter_by(id=account_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != user.id:
        return jsonify({"error": "Unauthorized access"}), 401
    return jsonify(account.as_dict()), 200

@account_blueprint.route("/edit_account/<account_id>", methods=["PUT"])
@jwt_required()
def edit_account(account_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    account = Accounts.query.filter_by(id=account_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    if "account_type" in data:
        account.account_type = data["account_type"]
    if "account_number" in data:
        account.account_number = data["account_number"]
    if "balance" in data:
        account.balance = data["balance"]
    account.updated_at = datetime.utcnow()
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify(account.as_dict()), 200

@account_blueprint.route("/delete_account/<account_id>", methods=["DELETE"])
@jwt_required()
def delete_account(account_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    account = Accounts.query.filter_by(id=account_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    try:    
        db.session.delete(account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Account deleted successfully"}), 200