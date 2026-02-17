import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

# ================= INIT =================

db = SQLAlchemy()

# ================= MODELS =================

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_name = db.Column(db.String(200))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)


# ================= APP FACTORY =================

def create_app():

    app = Flask(__name__)

    # SECRET KEY
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")

    # DATABASE (Supabase)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # ================= ADMIN LOGIN CONFIG =================

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


    # ================= LOGIN =================

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            username = request.form.get("username")
            password = request.form.get("password")

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

                session["admin"] = True

                return redirect("/admin/dashboard")

            flash("Invalid username or password")

        return render_template("login.html")


    # ================= LOGOUT =================

    @app.route("/logout")
    def logout():

        session.pop("admin", None)

        return redirect("/login")


    # ================= DASHBOARD =================

    @app.route("/")
    def home():

        if not session.get("admin"):
            return redirect("/login")

        return redirect("/admin/dashboard")


    @app.route("/admin/dashboard")
    def admin_dashboard():

        if not session.get("admin"):
            return redirect("/login")

        product_count = Product.query.count()
        order_count = Order.query.count()

        return render_template(
            "admin/dashboard.html",
            product_count=product_count,
            order_count=order_count
        )


    # ================= PRODUCTS =================

    @app.route("/admin/products")
    def admin_products():

        if not session.get("admin"):
            return redirect("/login")

        products = Product.query.all()

        return render_template(
            "admin/products.html",
            products=products
        )


    # ================= ORDERS =================

    @app.route("/admin/orders")
    def admin_orders():

        if not session.get("admin"):
            return redirect("/login")

        orders = Order.query.all()

        return render_template(
            "admin/orders.html",
            orders=orders
        )


    return app


# ================= RUN =================

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
