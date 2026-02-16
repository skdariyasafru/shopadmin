from flask import Flask, request, redirect, render_template, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import init_db, db
from db_init import create_tables
from models.models import User, Product, Cart, Order
from config import Config
import uuid

login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Init database
    init_db(app)

    with app.app_context():
        create_tables(app)

    # Init login manager
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = None


    # ✅ REQUIRED user_loader
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except:
            return None


    # Redirect unauthorized users to login popup
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/?login=1")


    # ================= HOME =================
    @app.route("/")
    def index():
        products = Product.query.all()
        return render_template("index.html", products=products)


    # ================= LOGIN =================
    @app.route("/login", methods=["POST"])
    def login():

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or user.password != password
