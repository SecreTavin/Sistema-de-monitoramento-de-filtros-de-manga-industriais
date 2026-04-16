import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

DATABASE_URI = os.getenv('DATABASE_URI')
SECRET_KEY = os.getenv('SECRET_KEY')

if not DATABASE_URI or not SECRET_KEY:
    raise ValueError("⚠️ ERRO CRÍTICO: Variável DATABASE_URI ou SECRET_KEY não encontrada. Verifique o ficheiro .env")


