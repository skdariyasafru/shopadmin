from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models.models import Product, Order
import os

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

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
                return redirect("/dashboard")

            flash("Invalid login")

        return render_template("login.html")


    # ================= LOGOUT =================

    @app.route("/logout")
    def logout():

        session.clear()
        return redirect("/login")


    # ================= DASHBOARD =================

    @app.route("/")
    @app.route("/dashboard")
    def dashboard():

        if not session.get("admin"):
            return redirect("/login")

        product_count = Product.query.count()
        order_count = Order.query.count()

        return render_template(
            "dashboard.html",
            product_count=product_count,
            order_count=order_count
        )


    # ================= VIEW PRODUCTS =================

    @app.route("/products")
    def products():

        if not session.get("admin"):
            return redirect("/login")

        products = Product.query.all()

        return render_template("products.html", products=products)


    # ================= ADD PRODUCT =================

    @app.route("/add_product", methods=["GET", "POST"])
    def add_product():

        if not session.get("admin"):
            return redirect("/login")

        if request.method == "POST":

            name = request.form.get("name")
            price = request.form.get("price")
            image = request.form.get("image")
            description = request.form.get("description")

            product = Product(
                name=name,
                price=price,
                image=image,
                description=description
            )

            db.session.add(product)
            db.session.commit()

            return redirect("/products")

        return render_template("add_product.html")


    # ================= DELETE PRODUCT =================

    @app.route("/delete_product/<int:id>")
    def delete_product(id):

        if not session.get("admin"):
            return redirect("/login")

        product = Product.query.get(id)

        if product:
            db.session.delete(product)
            db.session.commit()

        return redirect("/products")


    # ================= VIEW ORDERS =================

    @app.route("/orders")
    def orders():

        if not session.get("admin"):
            return redirect("/login")

        orders = Order.query.all()

        return render_template("orders.html", orders=orders)


    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
