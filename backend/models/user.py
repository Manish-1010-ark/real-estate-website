from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

def create_user_model(db):
    """Factory function to create User model with db instance"""
    
    class User(db.Model):
        __tablename__ = 'users'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(128), nullable=False)
        role = db.Column(db.String(20), nullable=False, default='buyer')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        is_active = db.Column(db.Boolean, default=True)
        
        def __init__(self, name, email, password, role='buyer'):
            self.name = name
            self.email = email
            self.set_password(password)
            self.role = role
            
        def set_password(self, password):
            """Hash and set password"""
            self.password_hash = generate_password_hash(password).decode('utf-8')
            
        def check_password(self, password):
            """Check if provided password matches hash"""
            return check_password_hash(self.password_hash, password)
        
        def is_admin(self):
            """Check if user is admin"""
            return self.role == 'admin'
        
        def is_agent(self):
            """Check if user is agent"""
            return self.role == 'agent'
        
        def is_buyer(self):
            """Check if user is buyer"""
            return self.role == 'buyer'
        
        def to_dict(self):
            """Convert user object to dictionary for JSON responses"""
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role,
                'created_at': self.created_at.isoformat(),
                'is_active': self.is_active
            }
        
        def __repr__(self):
            return f'<User {self.email}>'
    
    return User