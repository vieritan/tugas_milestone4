from flask import Flask # type: ignore
from flask_jwt_extended import JWTManager
from app.connectors.db import db
from app.controllers import user_route, account_route, transactions_route
from app.models.user import Users
from app.models.account import Accounts
from app.models.transactions import Transactions
import os

app = Flask(__name__)

DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_NAME = os.getenv("DATABASE_NAME")

SECRET_KEY = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = f"{DATABASE_TYPE}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = SECRET_KEY 

jwt = JWTManager(app)
db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(user_route.user_blueprint, url_prefix="/user")
app.register_blueprint(account_route.account_blueprint, url_prefix="/account")
app.register_blueprint(transactions_route.transactions_blueprint, url_prefix="/transactions")

@app.route('/')
def home():
    try:
        # Hanya cek apakah session dapat dibuat tanpa melakukan query
        db.session.commit()  # Hanya untuk memastikan tidak ada error saat terhubung
        return "Connected to the database!"
    except Exception as e:
        return f"Failed to connect to the database: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)