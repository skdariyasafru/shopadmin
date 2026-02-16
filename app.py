
from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import init_db, db
from db_init import create_tables
from models.models import User, Product, Cart, Order
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    init_db(app)
    create_tables(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/")

    @app.route("/")
    def index():
        products = Product.query.all()
        return render_template("index.html", products=products)

    @app.route("/login", methods=["POST"])
    def login():
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect("/")

        flash("Invalid login")
        return redirect("/")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route("/cart")
    @login_required
    def cart():
        items = Cart.query.filter_by(user_id=current_user.id).all()
        return render_template("cart.html", items=items)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
