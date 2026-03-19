from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy import text
from backend.config import Config
from backend.database import db
from backend.models import User, Category, Product, Order, OrderItem, Cart, CartItem
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from backend.routes.auth import auth_bp
from backend.routes.cart import cart_bp
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from backend.routes.auth import auth_bp, mail, oauth
from backend.models import User, Category, Product, Order, OrderItem, Cart, CartItem, Address



def create_app():
    # ---------Obtener la ruta base del proyecto-------------
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_folder = os.path.join(base_dir, 'frontend', 'templates')
    static_folder = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, static_url_path='/static')
    
    app.config.from_object(Config)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  
    app.config['SESSION_COOKIE_SECURE'] = False 
    CORS(app)
    
    # Configuración de subida (Asegúrate de que la ruta sea absoluta para evitar fallos)
    UPLOAD_FOLDER = os.path.join(static_folder, 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # ---------Inicialización de extensiones-----------------
    db.init_app(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'tu@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tu_app_password'  # App Password, no tu contraseña normal
    app.config['MAIL_DEFAULT_SENDER'] = 'tu@gmail.com'

    mail.init_app(app)
    oauth.init_app(app)
     
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    
    with app.app_context():
        db.create_all()
        print("¡Tablas sincronizadas en PostgreSQL!")

    # ---------Rutas de la API y Vistas-----------------

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
        # Traemos los productos de la DB para que se vean en el Home
        productos_db = Product.query.all()
        return render_template('public/home.html', productos=productos_db)
    @app.route('/perfil')
    def perfil():
        return render_template('public/perfil.html')

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
        
    @app.route("/catalogo")
    def catalogo():
        todos_los_productos = Product.query.all()
        return render_template('public/catalogo.html', productos=todos_los_productos)
    
    @app.route('/checkout')
    def checkout_view():
        return render_template('public/checkout.html')    
    
    @app.route('/direcciones')
    def direcciones_view():
        return render_template('public/direcciones.html')

    @app.route('/api/orders/checkout', methods=['POST'])
    @jwt_required()
    def checkout():
        user_id = get_jwt_identity()
        cart = Cart.query.filter_by(user_id=user_id).first()

        if not cart or len(cart.items) == 0:
            return jsonify({"msg": "El carrito está vacío"}), 400

        try:
            total_pago = 0
            for item in cart.items:
                producto = Product.query.get(item.product_id)
                print("PRODUCTO:", producto, "PRECIO:", producto.price if producto else "None")
                if producto:
                    total_pago += producto.price * item.quantity

            print("TOTAL CALCULADO:", total_pago)

            nueva_orden = Order(
                user_id=user_id,
                total_price=total_pago,
                status='pendiente',
            )
            db.session.add(nueva_orden)
            db.session.flush()

            for item in cart.items:
                producto = Product.query.get(item.product_id)
                detalle = OrderItem(
                    order_id=nueva_orden.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=producto.price
                )
                db.session.add(detalle)
                db.session.delete(item)

            db.session.commit()
            return jsonify({"msg": "Compra realizada", "order_id": nueva_orden.id}), 201

        except Exception as e:
            db.session.rollback()
            print("ERROR EN CHECKOUT:", str(e))
            return jsonify({"msg": "Error interno", "error": str(e)}), 500
            
    @app.route('/pedido-confirmado')
    def pedido_confirmado():
        return render_template('public/producto_confirmado.html')
    
    @app.route('/api/orders/mis-pedidos', methods=['GET'])
    @jwt_required()
    def mis_pedidos():
        user_id = get_jwt_identity()
        ordenes = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

        resultado = []
        for orden in ordenes:
            items = []
            for item in orden.items:
                producto = Product.query.get(item.product_id)
                items.append({
                    'product_name': producto.name if producto else 'Producto eliminado',
                    'image_url':    producto.image_url if producto else '',
                    'quantity':     item.quantity,
                    'price':        float(item.price_at_purchase),
                    'subtotal':     float(item.price_at_purchase * item.quantity),
                })
            resultado.append({
                'id':         orden.id,
                'fecha':      orden.created_at.strftime('%d/%m/%Y'),
                'total':      float(orden.total_price),
                'status':     orden.status,
                'items':      items,
            })

        return jsonify(resultado), 200
    
    @app.route('/pedidos')
    def pedidos_view():
        return render_template('public/pedidos.html')
    
    @app.route('/informacion')
    def informacion_view():
        return render_template('public/informacion.html')

    # ---------Rutas de Administración-------------

    @app.route('/admin/productos')
    def admin_productos():
        return render_template('admin/products.html')

    @app.route('/admin/agregar-producto', methods=['POST'])
    def agregar_producto():
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        categoria = request.form.get('categoria')
        file = request.files.get('imagen')
        
        descripcion = request.form.get('descripcion', 'Sin descripción')
        stock = request.form.get('stock', 10)

        if not file or not nombre or not precio:
            flash("Todos los campos son obligatorios")
            return redirect(url_for('admin_productos'))

        filename = secure_filename(file.filename)
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        nuevo_producto = Product(
            name=nombre,
            description=descripcion,
            price=float(precio),
            stock=int(stock),        
            image_url=filename,
            category_id=1
        )

        try:
            db.session.add(nuevo_producto)
            db.session.commit()
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}", 500

    return app 

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)