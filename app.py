
from flask import Flask, request, redirect, render_template, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()
login_manager = LoginManager()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    image = db.Column(db.String(500))
    description = db.Column(db.String(500))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    product_name = db.Column(db.String(200))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
    status = db.Column(db.String(50), default="Pending")

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        products = Product.query.all()
        return render_template("index.html", products=products)

    # ADMIN LOGIN
    @app.route("/admin", methods=["GET","POST"])
    def admin():
        if request.method=="POST":
            if request.form["username"]==ADMIN_USERNAME and request.form["password"]==ADMIN_PASSWORD:
                session["admin"]=True
                return redirect("/admin/dashboard")
            flash("Invalid login")
        return render_template("admin/login.html")

    # DASHBOARD
    @app.route("/admin/dashboard")
    def dashboard():
        if not session.get("admin"):
            return redirect("/admin")
        products = Product.query.all()
        orders = Order.query.all()
        return render_template("admin/dashboard.html", products=products, orders=orders)

    # ADD PRODUCT
    @app.route("/admin/add_product", methods=["GET","POST"])
    def add_product():
        if not session.get("admin"):
            return redirect("/admin")
        if request.method=="POST":
            p = Product(
                name=request.form["name"],
                price=request.form["price"],
                image=request.form["image"],
                description=request.form["description"]
            )
            db.session.add(p)
            db.session.commit()
            flash("Product added")
            return redirect("/admin/dashboard")
        return render_template("admin/add_product.html")

    # DELETE PRODUCT
    @app.route("/admin/delete_product/<int:id>")
    def delete_product(id):
        if not session.get("admin"):
            return redirect("/admin")
        p=Product.query.get(id)
        db.session.delete(p)
        db.session.commit()
        flash("Deleted")
        return redirect("/admin/dashboard")

    # UPDATE ORDER STATUS
    @app.route("/admin/update_order/<int:id>/<status>")
    def update_order(id,status):
        if not session.get("admin"):
            return redirect("/admin")
        o=Order.query.get(id)
        o.status=status
        db.session.commit()
        flash("Updated")
        return redirect("/admin/dashboard")

    return app

app=create_app()

if __name__=="__main__":
    app.run()
