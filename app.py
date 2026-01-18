from flask import Flask, jsonify, request, make_response, g
from flask_cors import CORS
import os
from psycopg2 import pool
from dotenv import load_dotenv
import uuid
import langchain_deepagent as agent
from apis.service_apis import create_service_blueprint
from apis.incident_apis import create_incident_blueprint
from apis.login_apis import create_login_blueprint
from apis.chat_apis import create_chat_blueprint

load_dotenv()

# Initialize connection pool
# Using smaller pool size to avoid OOM issues on Cloud Run
try:
    db_pool = pool.SimpleConnectionPool(
        1,  # minconn
        3,  # maxconn - reduced for Cloud Run memory constraints
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
except Exception as e:
    print(f"Error creating connection pool: {e}")
    db_pool = None

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://itsm-frontend.web.app"]}}, supports_credentials=True)

service_bp = create_service_blueprint(db_pool, agent)
incident_bp = create_incident_blueprint(db_pool, agent)
login_bp = create_login_blueprint()
chat_bp = create_chat_blueprint(db_pool, agent)

app.register_blueprint(service_bp)
app.register_blueprint(incident_bp)
app.register_blueprint(login_bp)    
app.register_blueprint(chat_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))