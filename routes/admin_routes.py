# routes/admin_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import uuid
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Blueprint
admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates')

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'realestate_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Password'),
    'port': os.getenv('DB_PORT', '5432')
}

# ==================== UTILITY FUNCTIONS ====================
def is_admin():
    identity = get_jwt_identity()
    # log for debugging
    print(f"[DEBUG is_admin] identity={identity!r}, type={type(identity)}, "
          f"role_claim={identity.get('role') if isinstance(identity, dict) else None}")
    
    if isinstance(identity, dict):
        return identity.get('role') == 'admin'
    return identity == os.getenv('ADMIN_USERNAME', 'admin')

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize the database with properties table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                price NUMERIC(12,2) NOT NULL,
                location VARCHAR(255) NOT NULL,
                bedrooms INTEGER NOT NULL,
                bathrooms INTEGER NOT NULL,
                area NUMERIC(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'Inactive',
                image TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
        
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")
        raise

# ==================== AUTHENTICATION ROUTES ====================
@admin_bp.route('/api/login', methods=['POST'])
def login():
    """Login endpoint that returns JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Use environment variables for credentials
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            # Create JWT token
            access_token = create_access_token(identity={"username": username, "role": "admin"})
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'user': username,
                'redirect': '/admin/dashboard'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login error: {str(e)}'
        }), 500

@admin_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint (client should discard token)"""
    current_user = get_jwt_identity()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@admin_bp.route('/api/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if the current token is valid"""
    user = get_jwt_identity()
    return jsonify({
        'success': True,
        'user': user,
        'message': 'Token is valid'
    })

# ==================== PROPERTIES API ROUTES ====================
@admin_bp.route('/properties', methods=['GET'])
@jwt_required()
def get_properties():
    """Get all properties (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403
    
    try:
        current_user = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM properties ORDER BY updated_at DESC')
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries
        properties_list = []
        for prop in properties:
            properties_list.append({
                'id': str(prop['id']),
                'title': prop['title'],
                'price': float(prop['price']),
                'location': prop['location'],
                'bedrooms': int(prop['bedrooms']),
                'bathrooms': int(prop['bathrooms']),
                'area': float(prop['area']),
                'status': prop['status'],
                'image': prop['image'],
                'created_at': prop['created_at'].isoformat() if prop['created_at'] else None,
                'updated_at': prop['updated_at'].isoformat() if prop['updated_at'] else None
            })
        
        return jsonify({
            'success': True,
            'data': properties_list,
            'count': len(properties_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching properties: {str(e)}'
        }), 500

@admin_bp.route('/properties/<property_id>', methods=['GET'])
@jwt_required()
def get_property(property_id):
    """Get a single property by ID (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403
    
    try:
        current_user = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM properties WHERE id = %s', (property_id,))
        property_data = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not property_data:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        property_dict = {
            'id': str(property_data['id']),
            'title': property_data['title'],
            'price': float(property_data['price']),
            'location': property_data['location'],
            'bedrooms': int(property_data['bedrooms']),
            'bathrooms': int(property_data['bathrooms']),
            'area': float(property_data['area']),
            'status': property_data['status'],
            'image': property_data['image'],
            'created_at': property_data['created_at'].isoformat() if property_data['created_at'] else None,
            'updated_at': property_data['updated_at'].isoformat() if property_data['updated_at'] else None
        }
        
        return jsonify({
            'success': True,
            'data': {
                'property': property_dict
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching property: {str(e)}'
        }), 500

@admin_bp.route('/properties', methods=['POST'])
@jwt_required()
def add_property():
    """Add a new property (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403

    try:
        # Required fields
        required = ['title','price','location','bedrooms','bathrooms','area','status']
        for f in required:
            if not request.form.get(f, '').strip():
                return jsonify({'success': False, 'message': f'Missing required field: {f}'}), 400

        # Parse numbers
        try:
            price    = float(request.form['price'])
            bedrooms = int(request.form['bedrooms'])
            bathrooms= int(request.form['bathrooms'])
            area     = float(request.form['area'])
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid numeric values provided'}), 400

        # Handle image upload
        image_filename = None
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.',1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            image_filename = filename

        # Insert into DB
        prop_id = str(uuid.uuid4())
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO properties
              (id,title,price,location,bedrooms,bathrooms,area,status,image,updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """, (
            prop_id,
            request.form['title'].strip(),
            price,
            request.form['location'].strip(),
            bedrooms,
            bathrooms,
            area,
            request.form['status'].strip(),
            image_filename
        ))
        conn.commit()
        cur.close(); conn.close()

        return jsonify({'success': True,'message':'Property added','data':{'id':prop_id}}), 201

    except Exception as e:
        return jsonify({'success':False,'message':f'Error adding property: {e}'}), 500


@admin_bp.route('/properties/<property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):
    """Update an existing property (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403

    try:
        conn = get_db_connection()
        cur  = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch existing
        cur.execute("SELECT * FROM properties WHERE id=%s", (property_id,))
        existing = cur.fetchone()
        if not existing:
            cur.close(); conn.close()
            return jsonify({'success':False,'message':'Property not found'}),404

        # Required fields
        required = ['title','price','location','bedrooms','bathrooms','area','status']
        for f in required:
            if not request.form.get(f, '').strip():
                cur.close(); conn.close()
                return jsonify({'success':False,'message':f'Missing required field: {f}'}),400

        # Parse numbers
        try:
            price    = float(request.form['price'])
            bedrooms = int(request.form['bedrooms'])
            bathrooms= int(request.form['bathrooms'])
            area     = float(request.form['area'])
        except ValueError:
            cur.close(); conn.close()
            return jsonify({'success':False,'message':'Invalid numeric values provided'}),400

        # Handle image upload
        image_filename = existing['image']  # keep old filename
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            # Remove old file
            if image_filename:
                old = os.path.join(UPLOAD_FOLDER, image_filename)
                if os.path.exists(old):
                    try: os.remove(old)
                    except: pass

            # Save new file
            ext = file.filename.rsplit('.',1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            image_filename = filename

        # Update DB
        cur.execute("""
            UPDATE properties SET
              title=%s, price=%s, location=%s,
              bedrooms=%s, bathrooms=%s, area=%s,
              status=%s, image=%s, updated_at=NOW()
            WHERE id=%s
        """, (
            request.form['title'].strip(),
            price,
            request.form['location'].strip(),
            bedrooms,
            bathrooms,
            area,
            request.form['status'].strip(),
            image_filename,
            property_id
        ))
        conn.commit()
        cur.close(); conn.close()

        return jsonify({'success':True,'message':'Property updated successfully'}), 200

    except Exception as e:
        return jsonify({'success':False,'message':f'Error updating property: {e}'}),500

@admin_bp.route('/properties/<property_id>/status', methods=['PATCH'])
@jwt_required()
def update_property_status(property_id):
    """Update property status (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403
    
    try:
        current_user = get_jwt_identity()
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        status = data['status']
        if status not in ['Active', 'Inactive']:
            return jsonify({
                'success': False,
                'message': 'Status must be either "Active" or "Inactive"'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE properties SET status = %s, updated_at = NOW() WHERE id = %s',
            (status, property_id)
        )
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Property status updated to {status}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating status: {str(e)}'
        }), 500

@admin_bp.route('/properties/<property_id>', methods=['DELETE'])
@jwt_required()
def delete_property(property_id):
    """Delete a property (admin only)"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Admins only'}), 403
    
    try:
        current_user = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get property to delete associated image
        cursor.execute('SELECT image FROM properties WHERE id = %s', (property_id,))
        property_data = cursor.fetchone()
        
        if not property_data:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Delete the property from database
        cursor.execute('DELETE FROM properties WHERE id = %s', (property_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Delete associated image file
        if property_data['image'] and os.path.exists(f".{property_data['image']}"):
            try:
                os.remove(f".{property_data['image']}")
            except Exception as e:
                print(f"Could not delete image file: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Property deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting property: {str(e)}'
        }), 500

# ==================== ADMIN DASHBOARD ROUTES ====================
@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard route"""
    return render_template('admin-dashboard.html')

@admin_bp.route('/admin')
def admin_dashboard_redirect():
    """Admin dashboard redirect route"""
    return redirect(url_for('admin_bp.admin_dashboard'))

# ==================== LEGACY & REDIRECT ROUTES ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def legacy_login():
    """Legacy login route - redirects to admin dashboard"""
    return redirect(url_for('admin_bp.admin_dashboard'))

@admin_bp.route('/')
def index():
    """Root route redirect"""
    return redirect(url_for('admin_bp.admin_dashboard'))

# ==================== TEST & DEBUG ROUTES ====================
@admin_bp.route('/test')
def test():
    """Test route for debugging database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM properties')
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for prop in properties:
            prop_dict = dict(prop)
            # Convert UUID to string for JSON serialization
            if 'id' in prop_dict:
                prop_dict['id'] = str(prop_dict['id'])
            # Convert datetime objects to ISO format
            for key in ['created_at', 'updated_at']:
                if key in prop_dict and prop_dict[key]:
                    prop_dict[key] = prop_dict[key].isoformat()
            result.append(prop_dict)
        
        return jsonify({
            'success': True,
            'properties': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ==================== BLUEPRINT UTILITIES ====================
def register_admin_blueprint(app):
    """Register admin blueprint with the Flask app"""
    app.register_blueprint(admin_bp)
    
    # Initialize database when blueprint is registered
    with app.app_context():
        init_db()