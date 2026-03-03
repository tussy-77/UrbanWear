from backend.database import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relación 1 → N
    products = db.relationship(
        "Product",
        backref="category",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }