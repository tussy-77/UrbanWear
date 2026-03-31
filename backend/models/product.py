from backend.database import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.Text)
    sizes      = db.Column(db.String(100), nullable=True)  # ej: "S,M,L,XL"
    item_number = db.Column(db.String(50), nullable=True)
    destacado = db.Column(db.Boolean, default=False)
    esencial  = db.Column(db.Boolean, default=False)
    gender    = db.Column(db.String(10), default='unisex')  # 'hombre', 'mujer', 'unisex'
    

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    @property
    def image_src(self):
        if not self.image_url:
            return None
        if self.image_url.startswith('/') or self.image_url.startswith('http'):
            return self.image_url
        return f'/static/uploads/{self.image_url}'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "stock": self.stock,
            "image_url": self.image_url,
            "category": self.category.name if self.category else None
    }