from backend.database import db

class Cart(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Relación con los items del carrito
    
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    __tablename__ = "cart_items"
    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', 'size', name='uq_cart_item_cart_product_size'),
        # size es nullable y NULL != NULL en SQL, así que la constraint de arriba no
        # bloquea duplicados para productos sin talla; este índice parcial cubre ese caso.
        db.Index(
            'uq_cart_item_cart_product_no_size',
            'cart_id', 'product_id',
            unique=True,
            postgresql_where=db.text('size IS NULL'),
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    size = db.Column(db.String(20), nullable=True)

    product = db.relationship('Product')