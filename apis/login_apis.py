from flask import Blueprint, jsonify

def create_login_blueprint():

    login_bp = Blueprint('login', __name__)

    @login_bp.route('/login', methods=['POST', 'GET'])
    def login():
        return jsonify({'status': 'successful'}), 200
    
    return login_bp

    