from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY
from app.models import session

def create_app():
    #caminhos relativos para encontrar as pastas corretamente.
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.secret_key = SECRET_KEY
    
    CORS(app)

    # Importa as rotas e junta no app
    from app.routes import init_routes
    init_routes(app)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        session.remove()
            
    return app
