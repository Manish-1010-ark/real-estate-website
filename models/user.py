from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum('admin', 'agent', 'customer', name='user_roles'), 
                     nullable=False, default='customer')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self, include_sensitive=False):
        user_dict = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_sensitive:
            user_dict['password'] = self.password
        return user_dict

    def is_admin(self):
        return self.role == 'admin'

    def is_agent(self):
        return self.role == 'agent'

    def is_customer(self):
        return self.role == 'customer'

    @staticmethod
    def validate_role(role):
        return role in ['admin', 'agent', 'customer']
