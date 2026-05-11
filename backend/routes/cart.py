from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.database import db
from backend.models.cart import Cart, CartItem
from backend.models import Product

cart_bp = Blueprint('cart', __name__)

# --- 1. AÑADIR PRODUCTOS AL CARRITO ---
@cart_bp.route('/api/cart/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = data.get('size') or None

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "Producto no encontrado"}), 404

    if product.stock <= 0:
        return jsonify({"msg": "Este producto está agotado"}), 400

    if product.sizes and not size:
        return jsonify({"msg": "Debes seleccionar una talla"}), 400

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.flush()

    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id, size=size).first()
    cantidad_actual = item.quantity if item else 0

    if cantidad_actual + quantity > product.stock:
        disponible = product.stock - cantidad_actual
        if disponible <= 0:
            return jsonify({"msg": f"Ya tienes el máximo disponible ({product.stock}) en el carrito"}), 400
        return jsonify({"msg": f"Solo quedan {product.stock} unidades disponibles"}), 400

    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity, size=size)
        db.session.add(item)

    db.session.commit()
    return jsonify({"msg": "Producto añadido al carrito"}), 200

# --- 2. VER EL CONTENIDO DEL CARRITO ---
@cart_bp.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({"items": [], "total": 0}), 200

    items = []
    total = 0
    for item in cart.items:
        # Validar si el producto existe antes de calcular
        if item.product:
            subtotal = item.product.price * item.quantity
            total += subtotal
            items.append({
                "id": item.id,
                "product_name": item.product.name,
                "price": float(item.product.price),
                "quantity": item.quantity,
                "size": item.size,
                "subtotal": float(subtotal)
            })

    return jsonify({"items": items, "total": total}), 200

@cart_bp.route('/api/cart/remove/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    user_id = get_jwt_identity()
    # Buscamos el item que pertenezca al carrito del usuario actual
    item = CartItem.query.join(Cart).filter(
        Cart.user_id == user_id, 
        CartItem.id == item_id
    ).first()

    if not item:
        return jsonify({"msg": "Producto no encontrado en tu carrito"}), 404

    db.session.delete(item)
    db.session.commit()
    
    return jsonify({"msg": "Producto eliminado del carrito"}), 200