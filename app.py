from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
from extensions import db, bcrypt, jwt  # ✅ restore all extensions
from flask_migrate import Migrate
from routes.inquiry_routes import inquiry_bp
from models.user_enquiry import Inquiry
from routes.property_routes import property_bp
from extensions import mail
from routes.frontend import frontend_bp

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
    app.config.from_object('config.Config')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # ==================== MAIL CONFIGURATION ====================
    app.config['MAIL_SERVER'] = 'smtp.zoho.in'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'admin@wallstreetllp.com'           # Replace with Zoho Mail
    app.config['MAIL_PASSWORD'] = 'cEmPuRbYW8Gx' 
    
    # ==================== CORS CONFIGURATION ====================
    CORS(app, resources={r"/api/*": {"origins": "https://wallstreetllp.com"}}, supports_credentials=True)
    
    # ==================== EXTENSIONS INITIALIZATION ====================
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app) 
    migrate = Migrate(app, db) 

    # ==================== JWT ERROR HANDLERS ====================
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from flask import jsonify
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from flask import jsonify
        return jsonify({
            'success': False,
            'message': 'Authorization token is required'
        }), 401

    # ==================== HEALTH CHECK ROUTE ====================
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'API is running'}, 200

    # ==================== BLUEPRINT REGISTRATION ====================
    
    # Frontend routes
    from routes.frontend import frontend_bp
    app.register_blueprint(frontend_bp)

    # Authentication routes
    from routes.auth import auth_bp	
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Property routes
    from routes.property_routes import property_bp
    app.register_blueprint(property_bp)

    # Inquiry routes
    from routes.inquiry_routes import inquiry_bp
    app.register_blueprint(inquiry_bp, url_prefix='/api')

    # Admin routes (new blueprint)
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # ==================== DATABASE INITIALIZATION ====================
    with app.app_context():
        from models.user import User
        db.create_all()

        # Create default admin user for SQLAlchemy models
        if not User.query.filter_by(email='admin@realestate.com').first():
            admin_user = User(
                name='System Administrator',
                email='admin@realestate.com',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin created: admin@realestate.com / admin123")

        # Initialize PostgreSQL properties table (for admin blueprint)
        try:
            from routes.admin_routes import init_db
            init_db()
            print("✅ PostgreSQL properties table initialized")
        except Exception as e:
            print(f"⚠️  PostgreSQL initialization warning: {e}")

    return app

app = create_app()