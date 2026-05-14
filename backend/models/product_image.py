from backend.database import db


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    image_url = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, default=0)  # Orden de las imágenes
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
