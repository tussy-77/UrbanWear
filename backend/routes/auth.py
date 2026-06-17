from flask import Blueprint, request, jsonify, redirect, url_for, current_app
from dotenv import load_dotenv
import os
import secrets
from datetime import datetime, timedelta
from backend.database import db
from backend.models.user import User, UserRole
from backend.models.otp import PendingOTPCode
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.address import Address
from backend.limiter import limiter
from backend.utils.validators import validate_password


load_dotenv()

auth_bp = Blueprint('auth', __name__)


mail = Mail()
oauth = OAuth()
s = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)



@auth_bp.route('/api/auth/register/send-code', methods=['POST'])
@limiter.limit("3 per minute")
def register_send_code():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'msg': 'El email es obligatorio'}), 400

    if User.query.filter_by(email=email).first():
        current_app.logger.info("register_send_code: email ya registrado '%s'", email)
        return jsonify({'msg': 'Si ese correo no está registrado, recibirás un código en breve.'}), 200

    code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    pending = PendingOTPCode.query.filter_by(email=email).first()
    if pending:
        pending.code = code
        pending.expires_at = expires_at
    else:
        db.session.add(PendingOTPCode(email=email, code=code, expires_at=expires_at))
    db.session.commit()

    from backend.utils.email import send_register_code
    send_register_code(mail, email, code)
    return jsonify({'msg': 'Si ese correo no está registrado, recibirás un código en breve.'}), 200


@auth_bp.route('/api/auth/register', methods=['POST'])
@limiter.limit("10 per minute")
def register():
    data = request.get_json() or {}
    email    = data.get('email', '').strip().lower()
    code     = data.get('code', '').strip()
    password = data.get('password', '')

    if not email or not code or not password:
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    pw_error = validate_password(password)
    if pw_error:
        return jsonify({"msg": pw_error}), 400

    pending = PendingOTPCode.query.filter_by(email=email).first()
    if not pending or pending.code != code:
        return jsonify({'msg': 'Código incorrecto'}), 400
    if pending.is_expired:
        db.session.delete(pending)
        db.session.commit()
        return jsonify({'msg': 'El código expiró. Solicita uno nuevo.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "El correo ya está registrado"}), 400

    name = data.get('name') or email.split('@')[0].replace('.', ' ').title()

    try:
        new_user = User(name=name, email=email, role=UserRole.customer)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.delete(pending)
        db.session.commit()

        from backend.utils.email import send_welcome
        send_welcome(mail, new_user)

        access_token = create_access_token(identity=str(new_user.id))
        return jsonify({
            "msg": "Usuario registrado con éxito",
            "access_token": access_token,
            "name": new_user.name,
            "user": new_user.to_dict()
        }), 201

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error en registro de usuario")
        return jsonify({"msg": "Error al registrar usuario"}), 500



@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
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
@limiter.limit("3 per minute")
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

@auth_bp.route('/api/auth/perfil', methods=['GET'])
@jwt_required()
def get_perfil():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify(user.to_dict()), 200

@auth_bp.route('/api/auth/direcciones', methods=['GET'])
@jwt_required()
def get_direcciones():
    user_id = get_jwt_identity()
    dirs = Address.query.filter_by(user_id=user_id).all()
    return jsonify([d.to_dict() for d in dirs]), 200

@auth_bp.route('/api/auth/direcciones', methods=['POST'])
@jwt_required()
def add_direccion():
    user_id = get_jwt_identity()
    data = request.get_json()

    nueva = Address(
        user_id    = user_id,
        department = data.get('department'),
        city       = data.get('city'),
        address    = data.get('address'),
        extra      = data.get('extra', ''),
        barrio     = data.get('barrio', ''),
        receiver   = data.get('receiver', ''),
        is_default = data.get('is_default', False)
    )
    db.session.add(nueva)
    db.session.commit()
    return jsonify({'msg': 'Dirección agregada', 'direccion': nueva.to_dict()}), 201

@auth_bp.route('/api/auth/direcciones/<int:dir_id>', methods=['DELETE'])
@jwt_required()
def delete_direccion(dir_id):
    user_id = get_jwt_identity()
    direccion = Address.query.filter_by(id=dir_id, user_id=user_id).first()
    if not direccion:
        return jsonify({'msg': 'Dirección no encontrada'}), 404
    db.session.delete(direccion)
    db.session.commit()
    return jsonify({'msg': 'Dirección eliminada'}), 200

@auth_bp.route('/api/auth/perfil', methods=['PUT'])
@jwt_required()
def update_perfil():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404

    data = request.get_json()
    user.name      = data.get('name', user.name)
    user.last_name = data.get('last_name', user.last_name)
    user.phone     = data.get('phone', user.phone)
    user.document  = data.get('document', user.document)
    user.gender    = data.get('gender', user.gender)

    birth = data.get('birth_date')
    if birth:
        from datetime import datetime
        user.birth_date = datetime.strptime(birth, '%Y-%m-%d').date()

    db.session.commit()
    return jsonify({'msg': 'Perfil actualizado', 'user': user.to_dict()}), 200


@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    email = (request.get_json() or {}).get('email', '').strip().lower()
    if not email:
        return jsonify({'msg': 'Ingresa tu email'}), 400
    user = User.query.filter_by(email=email).first()
    if user:
        token = s.dumps(email, salt='password-reset')
        link = url_for('reset_password_view', token=token, _external=True)
        from backend.utils.email import send_password_reset
        send_password_reset(mail, user, link)
    return jsonify({'msg': 'Si ese email está registrado recibirás un enlace en breve'}), 200


@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    password = data.get('password', '').strip()
    if not token or not password:
        return jsonify({'msg': 'Datos incompletos'}), 400
    pw_error = validate_password(password)
    if pw_error:
        return jsonify({'msg': pw_error}), 400
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        return jsonify({'msg': 'El enlace es inválido o ha expirado'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    user.set_password(password)
    db.session.commit()
    return jsonify({'msg': 'Contraseña actualizada. Ya puedes iniciar sesión.'}), 200


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
        user.set_password(secrets.token_hex(16))
        
        
        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return redirect(f'/?token={access_token}&name={nombre}')