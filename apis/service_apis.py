from flask import Blueprint, jsonify, request
from langgraph.types import Command

def create_service_blueprint(db_pool, agent):

    service_bp = Blueprint('service', __name__)

    @service_bp.route('/service-request', methods=['GET'])
    def list_service_request():
        if db_pool is None:
            return jsonify({'error': 'Database connection pool not available'}), 500
        
        conn = None
        try:
            conn = db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, status, action_taken, application, username, date_created FROM service_request ORDER BY id DESC")
            records = cursor.fetchall()
            
            service_requests = []
            for row in records:
                service_requests.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'action_taken': row[4],
                    'application': row[5],
                    'username': row[6],
                    'date_created': row[7].isoformat() if row[7] else None
                })
            
            cursor.close()
            db_pool.putconn(conn)
            return jsonify(service_requests)
        except Exception as e:
            if conn:
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500

    @service_bp.route('/service-request-make-decision', methods=['POST'])
    def make_decision():

        try:
            conn = db_pool.getconn()
            data = request.get_json()
            
            id = data.get('id')
            decision = data.get('decision')
            session_id = data.get('session_id')
            
            if not decision or not session_id:
                return jsonify({'error': 'Missing decision or session_id for interrupt response'}), 400
            
            agent_message = agent.make_decision(
                session_id,
                decision
            )

            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, application, username, status, action_taken FROM service_request WHERE id = %s",
                (id,)
            )
            updated_record = cursor.fetchone()
            cursor.close()
            db_pool.putconn(conn)
            
            return jsonify({
                'data': {
                    'id': updated_record[0],
                    'title': updated_record[1],
                    'description': updated_record[2],
                    'application': updated_record[3],
                    'username': updated_record[4],
                    'status': updated_record[5],
                    'action_taken': updated_record[6]
                },
                'message': agent_message
            }), 200
        except Exception as e:
            if conn:
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500

    @service_bp.route('/service-request', methods=['POST'])
    def create_service_request():
        if db_pool is None:
            return jsonify({'error': 'Database connection pool not available'}), 500
        
        conn = None
        try:
            conn = db_pool.getconn()
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'description', 'application', 'username']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            title = data['title']
            description = data['description']
            application = data['application']
            username = data['username']
            session_id = data['session_id'] if 'session_id' in data else None
            enable_ai_assistant = data.get('enable_ai_assistant', False)
            status = 'OPEN'
            
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO service_request (title, description, application, username, status, date_created) VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id, title, description, application, status",
                (title, description, application, username, status)
            )
            
            record = cursor.fetchone()
            conn.commit()
            cursor.close()

            agent_message = None
            if enable_ai_assistant:
                agent_message = agent.run("""
                    A new ITSM service request has been created with the following details:
                    ID: {id}
                    Title: {title}
                    Username: {username}
                    Description: {description}
                    Application: {application}
                    Status: {status}
                """.format(id=record[0], title=title, username=username, description=description, application=application, status=status), session_id=session_id)
            
            # Read the updated record after agent processing
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, application, username, status, action_taken FROM service_request WHERE id = %s",
                (record[0],)
            )
            updated_record = cursor.fetchone()
            cursor.close()
            db_pool.putconn(conn)
            
            return jsonify({
                'data': {
                    'id': updated_record[0],
                    'title': updated_record[1],
                    'description': updated_record[2],
                    'application': updated_record[3],
                    'username': updated_record[4],
                    'status': updated_record[5],
                    'action_taken': updated_record[6]
                },
                'message': agent_message
            }), 201
        except Exception as e:
            if conn:
                conn.rollback()
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500

    @service_bp.route('/service-request/<int:sr_id>', methods=['PUT'])
    def update_service_request(sr_id):
        if db_pool is None:
            return jsonify({'error': 'Database connection pool not available'}), 500
        
        conn = None
        try:
            conn = db_pool.getconn()
            data = request.get_json()
            
            # Build update fields dynamically - only allow specific fields
            allowed_fields = ['status', 'action_taken']
            update_fields = []
            update_values = []
            
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return jsonify({'error': 'No valid fields to update. Allowed fields: status, action_taken'}), 400
            
            update_values.append(sr_id)
            
            cursor = conn.cursor()
            query = f"UPDATE service_request SET {', '.join(update_fields)} WHERE id = %s RETURNING id, title, description, application, username, status, action_taken"
            cursor.execute(query, update_values)
            
            record = cursor.fetchone()
            
            if record is None:
                conn.rollback()
                cursor.close()
                db_pool.putconn(conn)
                return jsonify({'error': f'Service request with id {sr_id} not found'}), 404
            
            conn.commit()
            cursor.close()
            db_pool.putconn(conn)
            
            return jsonify({
                'data': {
                    'id': record[0],
                    'title': record[1],
                    'description': record[2],
                    'application': record[3],
                    'username': record[4],
                    'status': record[5],
                    'action_taken': record[6]
                },
                'message': 'Service request updated successfully'
            }), 200
        except Exception as e:
            if conn:
                conn.rollback()
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500
    
    return service_bp