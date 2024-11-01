from flask import Blueprint, jsonify, request
from app.models.user import Users
from app.models.account import Accounts
from app.models.transactions import Transactions
from app.connectors.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager # type: ignore

transactions_blueprint = Blueprint("transactions_blueprint", __name__)
jwt = JWTManager()

@transactions_blueprint.route("/", methods=["GET"])
def get_transactions():
    transactions = Transactions.query.all()
    return jsonify({"massage": "success"}), 200

@transactions_blueprint.route("/create_transaction/<account_id>", methods=["POST"])
@jwt_required()
def create_transaction(account_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    
    # Periksa apakah pengguna dan akun valid
    account = Accounts.query.filter_by(id=account_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != user.id:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.get_json()
    from_account_id = data.get("from_account_id")
    to_account_id = data.get("to_account_id")
    amount = data.get("amount")
    type = data.get("type")

    # Periksa input yang diperlukan
    # if not from_account_id or not to_account_id or not amount or not type:
    #     return jsonify({"error": "Missing required fields"}), 400

    try:
        # Jika tipe transaksi adalah "transfer"
        if type == "transfer":
            from_account = Accounts.query.filter_by(id=from_account_id).first()
            to_account = Accounts.query.filter_by(id=to_account_id).first()

            # Periksa apakah akun pengirim dan penerima valid
            if not from_account or not to_account:
                return jsonify({"error": "Account not found"}), 404

            # Periksa apakah saldo mencukupi di akun pengirim
            if from_account.balance < amount:
                return jsonify({"error": "Insufficient balance in from_account"}), 400

            # Kurangi saldo dari akun pengirim dan tambahkan ke akun penerima
            from_account.balance -= amount
            to_account.balance += amount

            # Tambahkan perubahan saldo akun ke sesi database
            db.session.add(from_account)
            db.session.add(to_account)
            
        if type == "withdraw":
            from_account = Accounts.query.filter_by(id=from_account_id).first()
            if not from_account:
                return jsonify({"error": "Account not found"}), 404
            if from_account.balance < amount:
                return jsonify({"error": "Insufficient balance"}), 400
            from_account.balance -= amount
            db.session.add(from_account)

        if type == "deposit":
            to_account = Accounts.query.filter_by(id=to_account_id).first()
            if not to_account:
                return jsonify({"error": "Account not found"}), 404
            to_account.balance += amount
            db.session.add(to_account)

        db.session.commit()

        # Buat transaksi baru
        new_transaction = Transactions(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            type=type,
            description=data.get("description"),
            created_at=datetime.utcnow()
        )
        
        # Simpan transaksi baru ke database
        db.session.add(new_transaction)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify(new_transaction.as_dict()), 201
    

@transactions_blueprint.route("/get_transactions_by_account/<account_id>", methods=["GET"])
@jwt_required()
def get_transactions_by_account(account_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    account = Accounts.query.filter_by(id=account_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != user.id:
        return jsonify({"error": "Unauthorized access"}), 401
    transactions = Transactions.query.filter_by(from_account_id=account_id).all()
    return jsonify([transaction.as_dict() for transaction in transactions]), 200

@transactions_blueprint.route("/get_transactions_by_id/<account_id>/<transaction_id>", methods=["GET"])
@jwt_required()
def get_transactions_by_id(account_id, transaction_id):
    identity = get_jwt_identity()
    user = Users.query.filter_by(id=identity).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    account = Accounts.query.filter_by(id=account_id).first()
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != user.id:
        return jsonify({"error": "Unauthorized access"}), 401
    transaction = Transactions.query.filter_by(id=transaction_id).first()
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404
    if transaction.from_account_id != account_id:
        return jsonify({"error": "Unauthorized access"}), 401
    
    return jsonify(transaction.as_dict()), 200