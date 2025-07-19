from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime
import re
from app import db, bcrypt
from models.user import User

auth_bp = Blueprint('auth', __name__)

ADMIN_EMAIL = "admin@wallstreetllp.com"

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['name', 'email', 'password', 'mobile']
    if not data or not all(f in data for f in required):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400

    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    phone = data['mobile'].strip()

    if len(name) < 2:
        return jsonify({'success': False, 'error': 'Name too short'}), 400

    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Invalid email'}), 400

    if not phone or len(phone) != 10:
        return jsonify({'success': False, 'error': 'Invalid phone'}), 400

    if email == ADMIN_EMAIL:
        return jsonify({'success': False, 'error': 'Email reserved for admin'}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 409

    is_valid, err = validate_password(password)
    if not is_valid:
        return jsonify({'success': False, 'error': err}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=name, email=email, password=hashed_password, phone=phone, role="customer")
    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'User registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    if email == "admin@wallstreetllp.com" and password == "Admin@123":
        access_token = create_access_token(identity=email, additional_claims={
            'id': 0, 'name': 'Administrator', 'email': email, 'role': 'admin', 'phone': ''
        })
        refresh_token = create_refresh_token(identity=email)
        return jsonify({
            'success': True,
            'message': 'Admin login successful',
            'data': {
                'user': {'id': 0, 'name': 'Administrator', 'email': email, 'role': 'admin', 'phone': ''},
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200

    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"❌ No user found with email: {email}")
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    if not user.password:
        print(f"❌ No password stored for user: {email}")
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    try:
        if not bcrypt.check_password_hash(user.password, password):
            print(f"❌ Password check failed for: {email}")
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        import traceback
        print("❌ Exception in password check:")
        traceback.print_exc()  # ✅ show full error
        return jsonify({'success': False, 'error': 'Internal error'}), 500


    access_token = create_access_token(identity=user.email, additional_claims={
        'id': user.id, 'name': user.name, 'email': user.email,
        'role': user.role, 'phone': user.phone
    })
    refresh_token = create_refresh_token(identity=user.email)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'phone': user.phone
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


from flask_jwt_extended import get_jwt

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    claims = get_jwt()  # fetch all user claims from the token
    return jsonify({
        'success': True,
        'user': claims,
        'message': 'Token is valid'
    })