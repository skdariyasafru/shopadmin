import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

# ================= INIT =================

db = SQLAlchemy()
login_manager = LoginManager()

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_name = db.Column(db.String(200))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)


# ================= APP FACTORY =================

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@host:5432/postgres"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # ================= USER LOADER =================

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ================= ADMIN LOGIN =================

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            username = request.form.get("username")
            password = request.form.get("password")

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

                session["admin"] = True

                return redirect("/admin/dashboard")

            flash("Invalid login")

        return render_template("admin/login.html")

    # ================= ADMIN DASHBOARD =================

    @app.route("/admin/dashboard")
    def dashboard():

        if not session.get("admin"):
            return redirect("/login")

        products = Product.query.all()
        orders = Order.query.all()

        return render_template(
            "admin/dashboard.html",
            products=products,
            orders=orders
        )

    # ================= ADMIN LOGOUT =================

    @app.route("/admin/logout")
    def logout():

        session.pop("admin", None)

        return redirect("/login")

    # ================= HOME =================

    @app.route("/")
    def home():

        products = Product.query.all()

        return render_template("admin/dashboard.html",
                               products=products,
                               orders=[])

    return app


# ================= RUN =================

app = create_app()

if __name__ == "__main__":
    app.run()
