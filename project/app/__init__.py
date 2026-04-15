from flask import Flask
from flask_cors import CORS

def create_app():
    #caminhos relativos para encontrar as pastas corretamente.
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    CORS(app)

    # Importa as rotas e junta no app
    from app.routes import init_routes
    init_routes(app)

    return app
