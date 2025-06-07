from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Create database tables
    with app.app_context():
        # Import and create models
        from models.user import create_user_model
        User = create_user_model(db)
        
        # Store User model globally for routes to use
        app.User = User
        
        db.create_all()
        print("Database tables created successfully!")

    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)