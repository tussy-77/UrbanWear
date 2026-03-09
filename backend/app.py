from flask import Flask, render_template, request, jsonify
from sqlalchemy import text
from backend.config import Config
from backend.database import db
from backend.models import User, Category, Product, Order, OrderItem, Cart, CartItem
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from backend.routes.auth import auth_bp
from flask_migrate import Migrate
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
    
    @app.route("/user_login")
    def cliente_login_view():
        return render_template('auth/user_login.html')

    @app.route("/user_register")
    def cliente_register_view():
        return render_template('auth/user_register.html')

    @app.route("/test-db")
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return "Database connected successfully!"
        except Exception as e:
            return str(e)

    @app.route('/api/orders/checkout', methods=['POST'])
    @jwt_required()
    def checkout():
        user_id = get_jwt_identity() # Ahora todo lo de abajo tiene el mismo nivel de espacios
    
        # 1. Buscar el carrito del usuario
        cart = Cart.query.filter_by(user_id=user_id).first()
        
        if not cart or not cart.items:
            return jsonify({"msg": "El carrito está vacío"}), 400

        try:
            # 2. Calcular el total y preparar la Orden
            total_pago = sum(item.product.price * item.quantity for item in cart.items)
            
            nueva_orden = Order(
                user_id=user_id,
                total_price=total_pago,
                status='completado'
            )
            db.session.add(nueva_orden)
            db.session.flush() 

            # 3. Mover items del Carrito a la Orden
            for item_carrito in cart.items:
                detalle_orden = OrderItem(
                    order_id=nueva_orden.id,
                    product_id=item_carrito.product_id,
                    quantity=item_carrito.quantity,
                    price_at_purchase=item_carrito.product.price
                )
                db.session.add(detalle_orden)

            # 4. VACIAR EL CARRITO
            for item_a_borrar in cart.items:
                db.session.delete(item_a_borrar)

            db.session.commit()
            return jsonify({
                "msg": "Compra realizada con éxito", 
                "order_id": nueva_orden.id,
                "total": total_pago
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error al procesar la compra", "error": str(e)}), 500

    return app 

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)