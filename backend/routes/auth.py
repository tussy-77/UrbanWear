from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models.user import User, UserRole
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    # Verificar si el usuario ya existe
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "El correo electrónico ya está registrado"}), 400

    try:
        # Crear nuevo usuario
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
            "user": user.to_dict()
        }), 200

    return jsonify({"msg": "Credenciales inválidas"}), 401
