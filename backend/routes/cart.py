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

    # Buscar o crear el carrito para este usuario
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Verificar si el producto ya está en el carrito
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
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
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal
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