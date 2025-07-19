from flask import Blueprint, request, jsonify
from models.user_enquiry import Inquiry
from models.property import Property
from extensions import db

inquiry_bp = Blueprint('inquiry', __name__)

@inquiry_bp.route('/inquiries', methods=['POST'])
def submit_inquiry():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    property_id = data.get("property_id")
    interested_in=data.get("interested_in")
    message=data.get("message")



    try:
        new_inquiry = Inquiry(
            name=name,
            email=email,
            phone=phone,
            property_id=property_id,
            interested_in=interested_in,
            message=message
        )
        db.session.add(new_inquiry)
        db.session.commit()
        return jsonify({"success": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
