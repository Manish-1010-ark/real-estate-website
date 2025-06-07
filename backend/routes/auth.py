from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    User = current_app.User
    data = request.get_json()
    if not data:
        return {'error': 'No data provided'}, 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'buyer').lower()

    if not all([name, email, password]) or not validate_email(email):
        return {'error': 'Invalid name/email/password'}, 400

    if not validate_password(password)[0]:
        return {'error': 'Weak password'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'User already exists'}, 409

    new_user = User(name=name, email=email, password=password, role=role)
    current_app.db.session.add(new_user)
    current_app.db.session.commit()

    token = create_access_token(identity=str(new_user.id), expires_delta=timedelta(hours=24))
    return {'message': 'User registered successfully', 'user': new_user.to_dict(), 'access_token': token}, 201

@auth_bp.route('/login', methods=['POST'])
def login():
    User = current_app.User
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'Invalid credentials'}, 401

    token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=24))
    return {'message': 'Login successful', 'user': user.to_dict(), 'access_token': token}, 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    User = current_app.User
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}, 404
    return {'user': user.to_dict()}, 200