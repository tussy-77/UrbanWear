from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import selectinload
from backend.database import db
from backend.models.wishlist import Wishlist
from backend.models.product import Product

wishlist_bp = Blueprint('wishlist', __name__)


@wishlist_bp.route('/api/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    items = Wishlist.query.filter_by(user_id=user_id).all()
    product_ids = [item.product_id for item in items]
    return jsonify({'ids': product_ids}), 200


@wishlist_bp.route('/api/wishlist/<int:product_id>', methods=['POST'])
@jwt_required()
def toggle_wishlist(product_id):
    user_id = get_jwt_identity()

    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'saved': False}), 200

    producto = Product.query.get(product_id)
    if not producto:
        return jsonify({'msg': 'Producto no encontrado'}), 404

    db.session.add(Wishlist(user_id=user_id, product_id=product_id))
    db.session.commit()
    return jsonify({'saved': True}), 200


@wishlist_bp.route('/api/wishlist/products', methods=['GET'])
@jwt_required()
def get_wishlist_products():
    user_id = get_jwt_identity()

    # Single JOIN + one selectinload for images — 2 queries regardless of wishlist size
    products = (
        Product.query
        .join(Wishlist, Wishlist.product_id == Product.id)
        .filter(Wishlist.user_id == user_id)
        .order_by(Wishlist.created_at.desc())
        .options(selectinload(Product.images))
        .all()
    )

    result = []
    for p in products:
        img = None
        if p.images:
            img = f'/static/uploads/{p.images[0].image_url}'
        elif p.image_url:
            img = p.image_url if p.image_url.startswith('/') or p.image_url.startswith('http') \
                else f'/static/uploads/{p.image_url}'
        result.append({
            'id':        p.id,
            'name':      p.name,
            'price':     float(p.price),
            'image_src': img,
            'gender':    p.gender,
        })

    return jsonify({'products': result}), 200
