from flask import Blueprint, request, jsonify, redirect, url_for
from dotenv import load_dotenv
import os
from backend.database import db
from backend.models.user import User, UserRole
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth

load_dotenv()

auth_bp = Blueprint('auth', __name__)


mail = Mail()
oauth = OAuth()
s = URLSafeTimedSerializer('CAMBIA_ESTO_POR_TU_SECRET_KEY')


s = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)



@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "El correo electrónico ya está registrado"}), 400

    try:
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            role=UserRole.customer
        )
        new_user.set_password(data.get('password'))
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "msg": "Usuario registrado con éxito",
            "user": new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al registrar: {str(e)}"}), 500



@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "msg": "Login exitoso",
            "access_token": access_token,
            "name": user.name,       
            "user": user.to_dict()   
        }), 200

    return jsonify({"msg": "Credenciales inválidas"}), 401



@auth_bp.route('/api/auth/magic-link', methods=['POST'])
def magic_link():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'msg': 'El email es obligatorio'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': 'No existe una cuenta con ese email.'}), 404

    token = s.dumps(email, salt='magic-login')
    link = url_for('auth.verificar_magic', token=token, _external=True)

    msg = Message('Tu acceso rápido — UrbanWear', recipients=[email])
    msg.html = f'''
        <div style="font-family:sans-serif; max-width:400px; margin:auto; padding:32px;">
            <h2 style="color:#111;">Hola, {user.name} 👋</h2>
            <p style="color:#555;">Haz clic para iniciar sesión. Válido por <strong>10 minutos</strong>:</p>
            <a href="{link}" style="display:inline-block; padding:12px 28px; background:#111;
               color:#fff; border-radius:8px; text-decoration:none; font-weight:bold;">
               Iniciar Sesión en UrbanWear
            </a>
            <p style="color:#aaa; font-size:0.8rem; margin-top:24px;">
                Si no solicitaste esto, ignora este email.
            </p>
        </div>
    '''
    mail.send(msg)
    return jsonify({'msg': 'Email enviado'}), 200



@auth_bp.route('/api/auth/magic-verify/<token>')
def verificar_magic(token):
    try:
        email = s.loads(token, salt='magic-login', max_age=600)  # 10 min
    except Exception:
        return 'Enlace inválido o expirado.', 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return 'Usuario no encontrado.', 404

    access_token = create_access_token(identity=str(user.id))
    # Redirige al home con el token en la URL — el JS lo captura y guarda
    return redirect(f'/?token={access_token}&name={user.name}')



@auth_bp.route('/api/auth/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)



@auth_bp.route('/api/auth/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    email = user_info['email']
    nombre = user_info.get('name', email)

    user = User.query.filter_by(email=email).first()
    if not user:
        
        user = User(
            email=email,
            name=nombre,
            role=UserRole.customer
        )
        import secrets
        user.set_password(secrets.token_hex(16))
        
        
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return redirect(f'/?token={access_token}&name={nombre}')