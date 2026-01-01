from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import util.db_util as db
from dotenv import load_dotenv
import langchain_deepagent as agent
from apis.service_apis import create_service_blueprint
from apis.incident_apis import create_incident_blueprint
from apis.login_apis import create_login_blueprint

load_dotenv()
db_conn = db.get_db_connection(os.getenv('DB_NAME'), os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'), os.getenv('DB_PORT'))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

service_bp = create_service_blueprint(db_conn, agent)
incident_bp = create_incident_blueprint(db_conn, agent)
login_bp = create_login_blueprint()

app.register_blueprint(service_bp)
app.register_blueprint(incident_bp)
app.register_blueprint(login_bp)    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))