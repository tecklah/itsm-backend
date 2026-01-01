from flask import Blueprint, jsonify, request

def create_incident_blueprint(db_pool, agent):

    incident_bp = Blueprint('incident', __name__)

    @incident_bp.route('/incident-ticket', methods=['GET'])
    def list_incident_ticket():
        if db_pool is None:
            return jsonify({'error': 'Database connection pool not available'}), 500
        
        conn = None
        try:
            conn = db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, status, resolution, application, username, date_created FROM incident_ticket ORDER BY id DESC")
            records = cursor.fetchall()
            
            incident_tickets = []
            for row in records:
                incident_tickets.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'status': row[3],
                    'resolution': row[4],
                    'application': row[5],
                    'username': row[6],
                    'date_created': row[7].isoformat() if row[7] else None
                })
            
            cursor.close()
            db_pool.putconn(conn)
            return jsonify(incident_tickets)
        except Exception as e:
            if conn:
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500

    @incident_bp.route('/incident-ticket', methods=['POST'])
    def create_incident_ticket():
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
            status = 'OPEN'
            
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO incident_ticket (title, description, application, username, status, date_created) VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id, title, description, application, status",
                (title, description, application, username, status)
            )
            
            record = cursor.fetchone()
            conn.commit()
            cursor.close()

            result = agent.run("""
                A new ITSM incident ticket has been created with the following details:
                ID: {id}
                Title: {title}
                Username: {username}
                Description: {description}
                Application: {application}
                Status: {status}
            """.format(id=record[0], title=title, username=username, description=description, application=application, status=status))
            
            # Read the updated record after agent processing
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, application, username, status, resolution FROM incident_ticket WHERE id = %s",
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
                    'resolution': updated_record[6]
                },
                'message': result.content
            }), 201
        except Exception as e:
            if conn:
                conn.rollback()
                db_pool.putconn(conn)
            return jsonify({'error': str(e)}), 500

    return incident_bp