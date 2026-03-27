from backend.database import db
from datetime import datetime


class Banner(db.Model):
    __tablename__ = 'banners'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False, default='Banner principal')
    position     = db.Column(db.String(20), default='editorial')  # 'hero' o 'editorial'
    image_url    = db.Column(db.Text, default='')

    tag          = db.Column(db.String(100), default='COLECCIÓN EXCLUSIVA')
    title        = db.Column(db.String(150), default='URBANWEAR')
    accent_word  = db.Column(db.String(60),  default='')   # palabra en naranja (solo hero)
    subtitle     = db.Column(db.String(200), default='Street Culture & Urban Design Corp.')
    description  = db.Column(db.String(300), default='Diseño Urbano & Cultura de Calle')
    badge1       = db.Column(db.String(150), default='Nueva Temporada • Edición Limitada')
    badge2       = db.Column(db.String(150), default='Piezas de Colección Especial')
    btn_text     = db.Column(db.String(60),  default='VER COLECCIÓN →')
    btn2_text    = db.Column(db.String(60),  default='NEW IN')   # segundo botón (solo hero)
    active       = db.Column(db.Boolean, default=True)

    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def image_src(self):
        if not self.image_url:
            return None
        if self.image_url.startswith('/') or self.image_url.startswith('http'):
            return self.image_url
        return f'/static/uploads/{self.image_url}'
