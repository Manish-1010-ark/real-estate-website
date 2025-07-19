from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.property import Property
from flask import make_response 
frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
@frontend_bp.route('/home')
def home():
    return render_template('home.html')

@frontend_bp.route('/properties')
def properties_page():
    return render_template('properties.html')

@frontend_bp.route('/about')
def about():
    return render_template('about.html')

@frontend_bp.route('/contact')
def contact():
    return render_template('contact.html')

@frontend_bp.route('/login')
def login():
    return render_template('login.html')

@frontend_bp.route('/admin/dashboard')
def admin():
    response = make_response(render_template('admin-dashboard.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

@frontend_bp.route('/property-detail.html')
def property_detail_page():
    return render_template('property-detail.html')

# ✅ NEW: Admin Properties Page
@frontend_bp.route('/admin/properties')
@login_required
def admin_properties():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    all_properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('admin_properties.html', properties=all_properties)
