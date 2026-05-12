from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from sqlalchemy import text
from backend.config import Config
from backend.database import db
from backend.models import User, Category, Product, Order, OrderItem, Cart, CartItem, ProductImage
import os
#import mercadopago
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from backend.routes.auth import auth_bp
from backend.routes.cart import cart_bp
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from backend.routes.auth import auth_bp, mail, oauth
from backend.models import User, Category, Product, Order, OrderItem, Cart, CartItem, Address, Banner
from backend.models.user import UserRole



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

    @app.route("/api/search")
    def search_products():
        q = request.args.get("q", "").strip()
        if not q:
            return jsonify({"products": []})
        results = Product.query.filter(Product.name.ilike(f"%{q}%")).limit(8).all()
        return jsonify({"products": [{
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "gender": p.gender,
            "image_src": p.image_src
        } for p in results]})

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
        if len(destacados) >= 4:
            productos_db = destacados
        elif destacados:
            ids_destacados = [p.id for p in destacados]
            relleno = Product.query.filter(
                ~Product.id.in_(ids_destacados)
            ).order_by(Product.id.desc()).limit(4 - len(destacados)).all()
            productos_db = destacados + relleno
        else:
            productos_db = Product.query.order_by(Product.id.desc()).limit(4).all()
        # Sección Essential: productos marcados como esencial
        esenciales = Product.query.filter_by(esencial=True).limit(4).all()
        if len(esenciales) < 4:
            ids_esenciales = [p.id for p in esenciales]
            ids_new_in = [p.id for p in productos_db]
            excluir = list(set(ids_esenciales + ids_new_in))
            relleno_e = Product.query.filter(
                ~Product.id.in_(excluir)
            ).order_by(Product.id.asc()).limit(4 - len(esenciales)).all()
            esenciales = esenciales + relleno_e

        hero_banner       = Banner.query.filter_by(active=True, position='hero').first()
        editorial         = Banner.query.filter_by(active=True, position='editorial').first()
        banner_secundario = Banner.query.filter_by(active=True, position='banner_secundario').first()
        banner_hombre     = Banner.query.filter_by(active=True, position='categoria_hombre').first()
        banner_mujer      = Banner.query.filter_by(active=True, position='categoria_mujer').first()
        return render_template('public/home.html', productos=productos_db,
                               esenciales=esenciales,
                               hero_banner=hero_banner, banner=editorial,
                               banner_secundario=banner_secundario,
                               banner_hombre=banner_hombre, banner_mujer=banner_mujer)

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
        genero_inicial = request.args.get('genero', 'hombre')
        return render_template('public/catalogo.html',
                               productos=todos_los_productos,
                               genero_inicial=genero_inicial)
    
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
            # Validar stock de todos los items antes de crear la orden
            items_snapshot = list(cart.items)
            for item in items_snapshot:
                producto = Product.query.get(item.product_id)
                if not producto:
                    return jsonify({"msg": f"Un producto del carrito ya no existe"}), 400
                if producto.stock < item.quantity:
                    if producto.stock == 0:
                        return jsonify({"msg": f'"{producto.name}" se agotó. Retíralo del carrito para continuar.'}), 400
                    return jsonify({"msg": f'Solo quedan {producto.stock} unidades de "{producto.name}".'}), 400

            total_pago = sum(
                Product.query.get(item.product_id).price * item.quantity
                for item in items_snapshot
            )

            nueva_orden = Order(
                user_id=user_id,
                total_price=total_pago,
                status='pendiente',
            )
            db.session.add(nueva_orden)
            db.session.flush()

            for item in items_snapshot:
                producto = Product.query.get(item.product_id)
                db.session.add(OrderItem(
                    order_id=nueva_orden.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_purchase=producto.price,
                    size=item.size
                ))
                producto.stock -= item.quantity
                db.session.delete(item)

            db.session.commit()
            return jsonify({"msg": "Compra realizada", "order_id": nueva_orden.id}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error interno", "error": str(e)}), 500
            
    @app.route('/pedido-confirmado')
    def pedido_confirmado():
        return render_template('public/producto_confirmado.html')

    # ── MercadoPago ──────────────────────────────────────────────────

    @app.route('/api/payment/create-preference', methods=['POST'])
    @jwt_required()
    def create_mp_preference():
        user_id = get_jwt_identity()
        data = request.get_json()
        order_id = data.get('order_id')

        order = Order.query.get(order_id)
        if not order or order.user_id != user_id:
            return jsonify({"msg": "Orden no encontrada"}), 404

        sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))

        items = []
        for item in order.items:
            product = Product.query.get(item.product_id)
            items.append({
                "title": product.name if product else "Producto UrbanWear",
                "quantity": int(item.quantity),
                "unit_price": float(item.price_at_purchase),
                "currency_id": "COP"
            })

        base_url = os.getenv("APP_BASE_URL", "http://127.0.0.1:5000")
        preference_data = {
            "items": items,
            "external_reference": str(order_id),
            "back_urls": {
                "success": f"{base_url}/pago-exitoso",
                "failure": f"{base_url}/pago-fallido",
                "pending": f"{base_url}/pago-pendiente"
            },
            "auto_return": "approved",
            "notification_url": f"{base_url}/api/payment/webhook",
            "statement_descriptor": "UrbanWear"
        }

        result = sdk.preference().create(preference_data)
        if result["status"] not in (200, 201):
            return jsonify({"msg": "Error al crear preferencia de pago", "detail": result.get("response")}), 500

        preference = result["response"]
        init_point = preference.get("sandbox_init_point") or preference.get("init_point")
        return jsonify({"init_point": init_point})

    @app.route('/api/payment/webhook', methods=['POST'])
    def mp_webhook():
        data = request.get_json(silent=True) or {}
        topic = data.get("type") or request.args.get("type")
        payment_id = (data.get("data") or {}).get("id") or request.args.get("data.id")

        if topic == "payment" and payment_id:
            try:
                sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN", ""))
                payment_info = sdk.payment().get(payment_id)
                payment = payment_info.get("response", {})
                order_id = payment.get("external_reference")
                status = payment.get("status")
                if order_id:
                    order = Order.query.get(int(order_id))
                    if order:
                        if status == "approved":
                            order.status = "pagado"
                        elif status == "rejected":
                            order.status = "cancelado"
                        db.session.commit()
            except Exception:
                pass

        return jsonify({"status": "ok"}), 200

    @app.route('/pago-exitoso')
    def pago_exitoso():
        order_id = request.args.get('external_reference')
        if order_id:
            try:
                order = Order.query.get(int(order_id))
                if order and order.status == 'pendiente':
                    order.status = 'pagado'
                    db.session.commit()
            except Exception:
                pass
        return render_template('public/pago_resultado.html', estado='exitoso', order_id=order_id)

    @app.route('/pago-fallido')
    def pago_fallido():
        order_id = request.args.get('external_reference')
        if order_id:
            try:
                order = Order.query.get(int(order_id))
                if order:
                    order.status = 'cancelado'
                    db.session.commit()
            except Exception:
                pass
        return render_template('public/pago_resultado.html', estado='fallido', order_id=order_id)

    @app.route('/pago-pendiente')
    def pago_pendiente():
        order_id = request.args.get('external_reference')
        return render_template('public/pago_resultado.html', estado='pendiente', order_id=order_id)
    
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
                    'size':         item.size,
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

   # ---------Autenticación de Administración-------------

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('admin_id'):
                return redirect(url_for('admin_login'))
            return f(*args, **kwargs)
        return decorated

    @app.route('/admin/login', methods=['GET'])
    def admin_login():
        if session.get('admin_id'):
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/login.html')

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login_api():
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        if not user or not user.check_password(data.get('password')):
            return jsonify({"msg": "Credenciales incorrectas"}), 401
        if user.role != UserRole.admin:
            return jsonify({"msg": "No tienes permisos de administrador"}), 403
        session['admin_id'] = user.id
        session['admin_name'] = user.name
        return jsonify({"msg": "ok"})

    @app.route('/api/admin/register', methods=['POST'])
    def admin_register_api():
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return jsonify({"msg": "Faltan datos obligatorios"}), 400

        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({"msg": "El correo electrónico ya está registrado"}), 400

        try:
            new_admin = User(
                name=data.get('name'),
                email=data.get('email'),
                role=UserRole.admin
            )
            new_admin.set_password(data.get('password'))
            db.session.add(new_admin)
            db.session.commit()

            return jsonify({
                "msg": "Cuenta de administrador creada con éxito",
                "user": new_admin.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": f"Error al crear la cuenta: {str(e)}"}), 500

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('admin_id', None)
        session.pop('admin_name', None)
        return redirect(url_for('admin_login'))

   # ---------Rutas de Administración-------------

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        from sqlalchemy import func, extract
        import json

        hoy = datetime.utcnow()

        # Métricas básicas
        total_productos    = Product.query.count()
        total_pedidos      = Order.query.count()
        total_usuarios     = User.query.count()
        total_ingresos     = db.session.query(func.sum(Order.total_price)).scalar() or 0
        pedidos_pendientes = Order.query.filter_by(status='pendiente').count()
        ticket_promedio    = db.session.query(func.avg(Order.total_price)).scalar() or 0

        # Últimas filas
        ultimos_pedidos  = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        ultimos_usuarios = User.query.order_by(User.created_at.desc()).limit(5).all()

        # Ventas por mes (últimos 6 meses)
        nombres_meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        meses_labels  = []
        meses_totales = []
        for i in range(5, -1, -1):
            mes  = ((hoy.month - 1 - i) % 12) + 1
            anio = hoy.year + ((hoy.month - 1 - i) // 12)
            total_mes = db.session.query(func.sum(Order.total_price)).filter(
                extract('month', Order.created_at) == mes,
                extract('year',  Order.created_at) == anio
            ).scalar() or 0
            meses_labels.append(nombres_meses[mes - 1])
            meses_totales.append(float(total_mes))

        # Pedidos por estado
        estados_raw    = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        estados_labels = [e[0].capitalize() for e in estados_raw]
        estados_valores = [e[1] for e in estados_raw]

        # Top 5 productos más vendidos
        top_productos = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_vendido'),
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('ingresos')
        ).join(OrderItem, OrderItem.product_id == Product.id
        ).group_by(Product.name
        ).order_by(func.sum(OrderItem.quantity).desc()
        ).limit(5).all()

        return render_template('admin/dashboard.html',
            total_productos    = total_productos,
            total_pedidos      = total_pedidos,
            total_usuarios     = total_usuarios,
            total_ingresos     = total_ingresos,
            pedidos_pendientes = pedidos_pendientes,
            ticket_promedio    = ticket_promedio,
            ultimos_pedidos    = ultimos_pedidos,
            ultimos_usuarios   = ultimos_usuarios,
            meses_labels       = json.dumps(meses_labels),
            meses_totales      = json.dumps(meses_totales),
            estados_labels     = json.dumps(estados_labels),
            estados_valores    = json.dumps(estados_valores),
            top_productos      = top_productos,
        )

    @app.route('/admin/productos')
    @admin_required
    def admin_productos():
        productos = Product.query.order_by(Product.id.desc()).all()
        return render_template('admin/products.html', productos=productos)

    @app.route('/admin/productos/agregar', methods=['POST'])
    @admin_required
    def admin_agregar_producto():
        nombre      = request.form.get('nombre')
        precio      = request.form.get('precio')
        descripcion = request.form.get('descripcion', '')
        stock       = request.form.get('stock', 10)
        tallas      = request.form.get('tallas', '')
        imagen_url  = request.form.get('imagen_url', '')
        files       = request.files.getlist('imagen')

        image_final = ''
        
        # Determinar imagen principal
        if files and files[0].filename:
            image_final = secure_filename(files[0].filename)
        elif imagen_url:
            image_final = imagen_url

        nuevo = Product(
            name        = nombre,
            description = descripcion,
            price       = float(precio),
            stock       = int(stock),
            image_url   = image_final,
            sizes       = tallas,
            gender      = request.form.get('genero', 'unisex'),
            category_id = 1
        )
        db.session.add(nuevo)
        db.session.commit()

        # Guardar todas las imágenes
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        for position, file in enumerate(files):
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product_image = ProductImage(
                    product_id=nuevo.id,
                    image_url=filename,
                    position=position
                )
                db.session.add(product_image)
        
        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/productos/editar/<int:product_id>', methods=['POST'])
    @admin_required
    def admin_editar_producto(product_id):
        producto             = Product.query.get_or_404(product_id)
        producto.name        = request.form.get('nombre')
        producto.price       = float(request.form.get('precio'))
        producto.description = request.form.get('descripcion', '')
        producto.stock       = int(request.form.get('stock', 10))
        producto.sizes       = request.form.get('tallas', '')
        producto.gender      = request.form.get('genero', 'unisex')

        imagen_url = request.form.get('imagen_url', '')
        files      = request.files.getlist('imagen')

        # Si hay nuevas imágenes, reemplazar todas
        if files and files[0].filename:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            # Eliminar imágenes antiguas
            ProductImage.query.filter_by(product_id=product_id).delete()
            
            # Guardar todas las nuevas imágenes
            for position, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    # La primera imagen es la imagen principal del producto
                    if position == 0:
                        producto.image_url = filename
                    
                    # Guardar en ProductImage
                    product_image = ProductImage(
                        product_id=product_id,
                        image_url=filename,
                        position=position
                    )
                    db.session.add(product_image)
        elif imagen_url:
            # Si solo cambia la URL externa
            producto.image_url = imagen_url

        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/productos/eliminar/<int:product_id>', methods=['POST'])
    @admin_required
    def admin_eliminar_producto(product_id):
        producto = Product.query.get_or_404(product_id)
        
        OrderItem.query.filter_by(product_id=product_id).delete()
        CartItem.query.filter_by(product_id=product_id).delete()
        
        
        db.session.delete(producto)
        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/pedidos')
    @admin_required
    def admin_pedidos():
        pedidos = Order.query.order_by(Order.created_at.desc()).all()
        return render_template('admin/orders.html', pedidos=pedidos)

    @app.route('/admin/pedidos/<int:order_id>/estado', methods=['POST'])
    @admin_required
    def admin_actualizar_estado(order_id):
        order = Order.query.get_or_404(order_id)
        nuevo_estado = (request.get_json() or {}).get('estado')
        estados_validos = ['pendiente', 'pagado', 'enviado', 'entregado', 'cancelado']
        if nuevo_estado not in estados_validos:
            return jsonify({"msg": "Estado inválido"}), 400
        order.status = nuevo_estado
        db.session.commit()
        return jsonify({"msg": "Estado actualizado", "estado": nuevo_estado})

    @app.route('/admin/usuarios')
    @admin_required
    def admin_usuarios():
        usuarios = User.query.order_by(User.created_at.desc()).all()
        return render_template('admin/customers.html', usuarios=usuarios)
    @app.route('/admin/productos/destacar/<int:product_id>', methods=['POST'])
    @admin_required
    def admin_destacar_producto(product_id):
        producto = Product.query.get_or_404(product_id)
        producto.destacado = not producto.destacado
        db.session.commit()
        return redirect(url_for('admin_productos'))

    @app.route('/admin/productos/esencial/<int:product_id>', methods=['POST'])
    @admin_required
    def admin_esencial_producto(product_id):
        producto = Product.query.get_or_404(product_id)
        producto.esencial = not producto.esencial
        db.session.commit()
        return redirect(url_for('admin_productos'))

    # ── Rutas Editorial (Banners) ──────────────────────────────────

    @app.route('/admin/editorial')
    @admin_required
    def admin_editorial():
        hero              = Banner.query.filter_by(position='hero').first()
        editorial         = Banner.query.filter_by(position='editorial').first()
        banner_secundario = Banner.query.filter_by(position='banner_secundario').first()
        cat_hombre        = Banner.query.filter_by(position='categoria_hombre').first()
        cat_mujer         = Banner.query.filter_by(position='categoria_mujer').first()
        if not hero:
            hero = Banner(
                name='Banner Hero (Portada)',
                position='hero',
                tag='Nueva Colección 2025',
                title='DEFINE TU ESTILO URBANO',
                accent_word='ESTILO',
                subtitle='Ropa diseñada para quienes no siguen tendencias — las crean.',
                btn_text='VER COLECCIÓN',
                btn2_text='NEW IN',
                description='', badge1='', badge2='',
            )
            db.session.add(hero)
        if not editorial:
            editorial = Banner(name='Banner Editorial', position='editorial')
            db.session.add(editorial)
        if not banner_secundario:
            banner_secundario = Banner(
                name='Banner Secundario',
                position='banner_secundario',
                tag='NUEVA COLECCIÓN',
                title='URBANWEAR',
                subtitle='Street Culture & Urban Design Corp.',
                description='Diseño Urbano & Cultura de Calle',
                badge1='', badge2='',
                btn_text='VER COLECCIÓN →',
            )
            db.session.add(banner_secundario)
        if not cat_hombre:
            cat_hombre = Banner(
                name='Categoría Hombre',
                position='categoria_hombre',
                tag='NUEVA COLECCIÓN',
                title='HOMBRE',
                subtitle='', description='', badge1='', badge2='',
                btn_text='VER COLECCIÓN →',
            )
            db.session.add(cat_hombre)
        if not cat_mujer:
            cat_mujer = Banner(
                name='Categoría Mujer',
                position='categoria_mujer',
                tag='NUEVA COLECCIÓN',
                title='MUJER',
                subtitle='', description='', badge1='', badge2='',
                btn_text='VER COLECCIÓN →',
            )
            db.session.add(cat_mujer)
        db.session.commit()
        return render_template('admin/editorial.html',
                               hero=hero, editorial=editorial,
                               banner_secundario=banner_secundario,
                               cat_hombre=cat_hombre, cat_mujer=cat_mujer)

    @app.route('/admin/editorial/guardar/<int:banner_id>', methods=['POST'])
    @admin_required
    def admin_guardar_banner(banner_id):
        banner = Banner.query.get_or_404(banner_id)
        banner.name        = request.form.get('name',        banner.name)
        banner.tag         = request.form.get('tag',         banner.tag)
        banner.title       = request.form.get('title',       banner.title)
        banner.accent_word = request.form.get('accent_word', banner.accent_word)
        banner.subtitle    = request.form.get('subtitle',    banner.subtitle)
        banner.description = request.form.get('description', banner.description)
        banner.badge1      = request.form.get('badge1',      banner.badge1)
        banner.badge2      = request.form.get('badge2',      banner.badge2)
        banner.btn_text    = request.form.get('btn_text',    banner.btn_text)
        banner.btn2_text   = request.form.get('btn2_text',   banner.btn2_text)
        banner.active      = request.form.get('active') == 'on'

        imagen_url = request.form.get('imagen_url', '').strip()
        file       = request.files.get('imagen')
        if file and file.filename:
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            banner.image_url = filename
        elif imagen_url:
            banner.image_url = imagen_url

        db.session.commit()
        return redirect(url_for('admin_editorial'))

    @app.route('/admin/editorial/nuevo', methods=['POST'])
    @admin_required
    def admin_nuevo_banner():
        banner = Banner(name=request.form.get('name', 'Nuevo banner'))
        db.session.add(banner)
        db.session.commit()
        return redirect(url_for('admin_editorial'))

    @app.route('/admin/editorial/eliminar/<int:banner_id>', methods=['POST'])
    @admin_required
    def admin_eliminar_banner(banner_id):
        banner = Banner.query.get_or_404(banner_id)
        db.session.delete(banner)
        db.session.commit()
        return redirect(url_for('admin_editorial'))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)