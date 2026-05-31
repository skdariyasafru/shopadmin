import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import threading
import time
import requests
from flask_login import LoginManager
from config import Config
from db import init_db
from models.models import User,Order,Product


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "super-secret-key"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    ADMIN_USERNAME = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    ADMIN_PASSWORD = os.getenv(
        "ADMIN_PASSWORD",
        "admin123"
    )

    # ================= LOGIN =================

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            username = request.form.get("username")
            password = request.form.get("password")

            if (
                username == ADMIN_USERNAME
                and password == ADMIN_PASSWORD
            ):

                session["admin"] = True

                return redirect("/admin/dashboard")

            flash("Invalid username or password")

        return render_template("login.html")

    # ================= LOGOUT =================

    @app.route("/logout")
    def logout():

        session.pop("admin", None)

        return redirect("/login")

    # ================= HOME =================

    @app.route("/")
    def home():

        if not session.get("admin"):
            return redirect("/login")

        return redirect("/admin/dashboard")

    # ================= DASHBOARD =================

    @app.route("/admin/dashboard")
    def admin_dashboard():

        if not session.get("admin"):
            return redirect("/login")

        product_count = Product.query.count()

        order_count = Order.query.count()

        pending_orders = Order.query.filter_by(
            status="Pending"
        ).count()

        delivered_orders = Order.query.filter_by(
            status="Delivered"
        ).count()

        paid_orders = Order.query.filter_by(
            payment_status="Paid"
        ).count()

        return render_template(
            "admin/dashboard.html",
            product_count=product_count,
            order_count=order_count,
            pending_orders=pending_orders,
            delivered_orders=delivered_orders,
            paid_orders=paid_orders
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

        orders = Order.query.order_by(
            Order.created_at.desc()
        ).all()

        return render_template(
            "admin/orders.html",
            orders=orders
        )

    # ================= MARK PAID =================

    @app.route("/admin/order/<int:id>/paid")
    def mark_paid(id):

        if not session.get("admin"):
            return redirect("/login")

        order = Order.query.get_or_404(id)

        order.payment_status = "Paid"

        db.session.commit()

        flash("Payment marked as Paid")

        return redirect("/admin/orders")

    # ================= MARK DELIVERED =================

    @app.route("/admin/order/<int:id>/delivered")
    def mark_delivered(id):

        if not session.get("admin"):
            return redirect("/login")

        order = Order.query.get_or_404(id)

        order.status = "Delivered"

        db.session.commit()

        flash("Order marked as Delivered")

        return redirect("/admin/orders")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
