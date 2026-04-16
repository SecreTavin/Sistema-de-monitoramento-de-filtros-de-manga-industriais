from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from config import DATABASE_URI

engine = create_engine(DATABASE_URI, pool_pre_ping=True, pool_recycle=3600)
session = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

Base = declarative_base()

# --- MODELOS DE BANCO DE DADOS ---
class Filtro(Base):
    __tablename__ = 'filtros'
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    ultima_manutencao = Column(Date)
    ultima_afericao_deltap = Column(Float)
    quantidade_mangas = Column(Integer)
    material_manga = Column(String(100))
    #Relatório de avarias (String)
    observacoes = Column(Text, default="Nenhuma avaria registrada.")

class LogFiltro(Base):
    __tablename__ = 'logs_filtros'
    id = Column(Integer, primary_key=True)
    filtro_id = Column(Integer)
    valor_deltap = Column(Float)
    status_anterior = Column(String(50))
    status_novo = Column(String(50))
    data_evento = Column(DateTime, default=datetime.now)

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# Cria as tabelas se não existirem
Base.metadata.create_all(engine)