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

    # Initialize database
    init_db(app)

    with app.app_context():
        create_tables(app)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = None


    # REQUIRED: user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # Redirect unauthorized users
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect("/?login=1")


    # ================= HOME =================
    @app.route("/")
    def index():

        search = request.args.get("q")

        if search:
            products = Product.query.filter(
                Product.name.ilike(f"%{search}%")
            ).all()
        else:
            products = Product.query.all()

        return render_template("index.html", products=products)


    # ================= LOGIN =================
    @app.route("/login", methods=["POST"])
    def login():

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if not user or user.password != password:
            flash("Invalid username or password")
            return redirect("/?login=1")

        login_user(user)
        flash("Login successful")

        return redirect("/")


    # ================= REGISTER =================
    @app.route("/register", methods=["POST"])
    def register():

        username = request.form.get("username")
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")

        existing = User.query.filter_by(username=username).first()

        if existing:
            flash("User already exists")
            return redirect("/?login=1")

        ref_code = str(uuid.uuid4())[:8]

        new_user = User(
            username=username,
            password=password,
            phone=phone,
            address=address,
            referral_code=ref_code,
            points=0
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful")

        return redirect("/?login=1")


    # ================= LOGOUT =================
    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        flash("Logged out")

        return redirect("/")


    # ================= ADD TO CART =================
    @app.route("/add_to_cart", methods=["POST"])
    def add_to_cart():

        if not current_user.is_authenticated:
            return jsonify({"status": "login_required"}), 401

        product_id = request.json.get("id")

        item = Cart.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if item:
            item.quantity += 1
        else:
            new_item = Cart(
                user_id=current_user.id,
                product_id=product_id,
                quantity=1
            )
            db.session.add(new_item)

        db.session.commit()

        return jsonify({"status": "added"})


    # ================= CART =================
    @app.route("/cart")
    @login_required
    def cart():

        cart_items = Cart.query.filter_by(user_id=current_user.id).all()

        items = []
        total = 0

        for item in cart_items:

            product = Product.query.get(item.product_id)

            subtotal = product.price * item.quantity

            total += subtotal

            items.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal
            })

        return render_template("cart.html", items=items, total=total)


    # ================= CHECKOUT =================
    @app.route("/checkout")
    @login_required
    def checkout():

        cart_items = Cart.query.filter_by(user_id=current_user.id).all()

        if not cart_items:
            flash("Cart empty")
            return redirect("/")

        for item in cart_items:

            product = Product.query.get(item.product_id)

            order = Order(
                username=current_user.username,
                phone=current_user.phone,
                address=current_user.address,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
                total=product.price * item.quantity
            )

            db.session.add(order)

        Cart.query.filter_by(user_id=current_user.id).delete()

        db.session.commit()

        flash("Order placed successfully")

        return redirect("/my_orders")


    # ================= MY ORDERS =================
    @app.route("/my_orders")
    @login_required
    def my_orders():

        orders = Order.query.filter_by(
            username=current_user.username
        ).all()

        return render_template("orders.html", orders=orders)


    return app


# Required for Gunicorn
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
