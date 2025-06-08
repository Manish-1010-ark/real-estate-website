from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os

from extensions import db, bcrypt, jwt  # Import shared instances

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///real_estate.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # ✅ Health check route
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'API is running'}, 200

    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Create tables and default admin user
    with app.app_context():
        from models.user import User
        db.create_all()

        # Only create admin if not already present
        if not User.query.filter_by(email='admin@realestate.com').first():
            admin_user = User(
                name='System Administrator',
                email='admin@realestate.com',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin user created: admin@realestate.com / admin123")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
