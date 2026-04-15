import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

DATABASE_URI = os.getenv('DATABASE_URI')

if not DATABASE_URI:
    raise ValueError("⚠️ ERRO CRÍTICO: Variável DATABASE_URI não encontrada. Verifique o ficheiro .env")

