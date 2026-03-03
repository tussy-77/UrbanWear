from flask import Flask, render_template
from sqlalchemy import text
from backend.config import Config
from backend.database import db
from backend.models import User
import os
from backend.models import User, Category, Product


def create_app():
    # Obtener la ruta base del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folder = os.path.join(base_dir, 'frontend', 'templates')
    static_folder = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, static_url_path='/static')
    app.config.from_object(Config)

    db.init_app(app)
    
    @app.route("/api/products")
    def get_products():
        products = Product.query.all()
        return {
            "products": [product.to_dict() for product in products]
    }

    @app.route("/")
    def home():
        return render_template('public/home.html')

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