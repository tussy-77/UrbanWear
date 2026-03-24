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
        destacados = Product.query.filter_by(destacado=True).limit(4).all()
        if len(destacados) < 4:
            productos_db = Product.query.order_by(Product.id.desc()).limit(4).all()
        else:
            productos_db = destacados
            return render_template('public/home.html', productos=productos_db)
        
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
    
    @app.route('/producto/<int:product_id>')
    def producto_detalle(product_id):
        producto = Product.query.get_or_404(product_id)
        return render_template('public/producto.html', producto=producto)

   # ---------Rutas de Administración-------------

    @app.route('/admin')
    def admin_dashboard():
        from sqlalchemy import func
        total_productos  = Product.query.count()
        total_pedidos    = Order.query.count()
        total_usuarios   = User.query.count()
        total_ingresos   = db.session.query(func.sum(Order.total_price)).scalar() or 0
        ultimos_pedidos  = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        ultimos_usuarios = User.query.order_by(User.created_at.desc()).limit(5).all()
        return render_template('admin/dashboard.html',
            total_productos  = total_productos,
            total_pedidos    = total_pedidos,
            total_usuarios   = total_usuarios,
            total_ingresos   = total_ingresos,
            ultimos_pedidos  = ultimos_pedidos,
            ultimos_usuarios = ultimos_usuarios
        )

    @app.route('/admin/productos')
    def admin_productos():
        productos = Product.query.order_by(Product.id.desc()).all()
        return render_template('admin/products.html', productos=productos)

    @app.route('/admin/productos/agregar', methods=['POST'])
    def admin_agregar_producto():
        nombre      = request.form.get('nombre')
        precio      = request.form.get('precio')
        descripcion = request.form.get('descripcion', '')
        stock       = request.form.get('stock', 10)
        tallas      = request.form.get('tallas', '')
        imagen_url  = request.form.get('imagen_url', '')
        file        = request.files.get('imagen')

        if file and file.filename:
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_final = filename
        elif imagen_url:
            image_final = imagen_url
        else:
            image_final = ''

        nuevo = Product(
            name        = nombre,
            description = descripcion,
            price       = float(precio),
            stock       = int(stock),
            image_url   = image_final,
            sizes       = tallas,
            category_id = 1
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/productos/editar/<int:product_id>', methods=['POST'])
    def admin_editar_producto(product_id):
        producto             = Product.query.get_or_404(product_id)
        producto.name        = request.form.get('nombre')
        producto.price       = float(request.form.get('precio'))
        producto.description = request.form.get('descripcion', '')
        producto.stock       = int(request.form.get('stock', 10))
        producto.sizes       = request.form.get('tallas', '')

        imagen_url = request.form.get('imagen_url', '')
        file       = request.files.get('imagen')

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.image_url = filename
        elif imagen_url:
            producto.image_url = imagen_url

        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/productos/eliminar/<int:product_id>', methods=['POST'])
    def admin_eliminar_producto(product_id):
        producto = Product.query.get_or_404(product_id)
        
        OrderItem.query.filter_by(product_id=product_id).delete()
        CartItem.query.filter_by(product_id=product_id).delete()
        
        
        db.session.delete(producto)
        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/pedidos')
    def admin_pedidos():
        pedidos = Order.query.order_by(Order.created_at.desc()).all()
        return render_template('admin/orders.html', pedidos=pedidos)

    @app.route('/admin/usuarios')
    def admin_usuarios():
        usuarios = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/customers.html', usuarios=usuarios)
    @app.route('/admin/productos/destacar/<int:product_id>', methods=['POST'])
    def admin_destacar_producto(product_id):
        producto = Product.query.get_or_404(product_id)
        producto.destacado = not producto.destacado
        db.session.commit()
        return redirect(url_for('admin_productos'))

    return app 

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)