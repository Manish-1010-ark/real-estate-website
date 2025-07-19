from flask import Blueprint, jsonify
from models.property import Property
from sqlalchemy import func

property_bp = Blueprint('property_bp', __name__)

# GET /api/properties — public list of active properties (case-insensitive)
@property_bp.route('/api/properties', methods=['GET'])
def get_all_active_properties():
    try:
        # Filter only status='active' (or 'Active', etc.), then sort by newest first
        properties = (
            Property.query
                    .filter(func.lower(Property.status) == 'active')
                    .order_by(Property.created_at.desc())
                    .all()
        )

        return jsonify({
            'success': True,
            'data': [prop.to_dict() for prop in properties]
        }), 200

    except Exception as e:
        print("❌ Error fetching properties:", str(e))
        return jsonify({'success': False, 'error': 'Failed to load properties'}), 500


# GET /api/properties/<id> — get property by ID
@property_bp.route('/api/properties/<string:property_id>', methods=['GET'])
def get_property_by_id(property_id):
    try:
        prop = Property.query.get(property_id)
        if not prop:
            return jsonify({'success': False, 'error': 'Property not found'}), 404

        return jsonify({'success': True, 'data': prop.to_dict()}), 200
    except Exception as e:
        print("❌ Error fetching property:", str(e))
        return jsonify({'success': False, 'error': 'Something went wrong'}), 500

@property_bp.route('/property-detail.html')
def property_page():
    return render_template('property-detail.html')