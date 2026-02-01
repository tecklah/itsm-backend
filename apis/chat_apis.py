from flask import Blueprint, jsonify, request

def create_chat_blueprint(db_pool, agent):

    chat_bp = Blueprint('chat', __name__)

    @chat_bp.route('/chat-request', methods=['POST'])
    def chat_request():
        
        data = request.get_json()
        
        # Check if this is a decision response for human-in-the-loop
        if data.get('type') == 'interrupt':
            decision = data.get('decision')
            session_id = data.get('session_id')
            
            if not decision or not session_id:
                return jsonify({'error': 'Missing decision or session_id for interrupt response'}), 400
            
            # Resume the agent with the decision
            result = agent.make_decision(session_id=session_id, decision=decision)
            
            print(f"Agent result1: {result}")

            # Check if result is another interrupt
            if isinstance(result, dict) and result.get('type') == 'interrupt':
                return jsonify(result), 200
            
            # Normal message response
            if isinstance(result, dict) and result.get('type') == 'message':
                message = result.get('message', '')
            elif hasattr(result, 'content'):
                message = result.content
            else:
                message = str(result)
            
            return jsonify({'message': message}), 200
        
        # Normal chat request
        # Validate required fields
        required_fields = ['question']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        question = data['question']
        username = data.get('username', '')
        session_id = data.get('session_id', None)

        result = agent.run("""
            A chat request has been created with the following details:
            Username: {username}
            Question: {question}
        """.format(question=question, username=username), session_id=session_id)
        
        print(f"Agent result: {result}")
        
        # Check if result is an interrupt (dict with 'type' key)
        if isinstance(result, dict) and result.get('type') == 'interrupt':
            return jsonify(result), 200
        
        # Normal message response
        if isinstance(result, dict) and result.get('type') == 'message':
            message = result.get('message', '')
        elif hasattr(result, 'content'):
            message = result.content
        else:
            message = str(result)
        
        return jsonify({'message': message}), 200
    
    return chat_bp

