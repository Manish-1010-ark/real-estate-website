from extensions import db
from datetime import datetime

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=True)  
    location = db.Column(db.String(255), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    area = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=True)  # optional
    #features = db.Column(db.Text, nullable=True)     # optional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(255), nullable=False)  # changed from image_urls

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'location': self.location,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'status': self.status,
            #'features': self.features.split(',') if self.features else [],
            'image': self.image,
            'created_at': self.created_at.isoformat()
        }
