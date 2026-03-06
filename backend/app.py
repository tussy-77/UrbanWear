from flask import Flask, render_template, request, jsonify # Añadido jsonify
from sqlalchemy import text
from backend.config import Config
from backend.database import db
from backend.models import User, Category, Product
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from backend.routes.auth import auth_bp
from flask_migrate import Migrate 
from backend.models.cart import Cart, CartItem
from backend.routes.cart import cart_bp
from flask_cors import CORS

def create_app():
    
    # ---------Obtener la ruta base del proyecto-------------
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folder = os.path.join(base_dir, 'frontend', 'templates')
    static_folder = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(Config)
    CORS(app)

    # ---------Inicialización de extensiones-----------------
    
    db.init_app(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    
    migrate = Migrate(app, db)
     
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    
    with app.app_context():
        db.create_all()
        print("¡Tablas del carrito creadas en PostgreSQL!")

    @app.route("/api/products")
    def get_products():
        category = request.args.get("category")
        query = Product.query
        if category:
            query = query.join(Category).filter(Category.name == category)
        products = query.all()
        return {
            "products": [product.to_dict() for product in products]
        }

    @app.route("/")
    def home():
        return render_template('public/home.html')

    @app.route("/login")
    def login_page():
        return render_template('auth/login.html')

    @app.route("/register")
    def register_page():
        return render_template('auth/register.html')

    @app.route("/test-db")
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return "Database connected successfully!"
        except Exception as e:
            return str(e)

    return app 

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)