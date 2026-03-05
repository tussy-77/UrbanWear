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
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    # Relación para obtener detalles del producto fácilmente
    
    product = db.relationship('Product')