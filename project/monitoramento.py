from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import mysql.connector
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
CORS(app)

Base = declarative_base()

class Filtro(Base):
    __tablename__ = 'filtros'
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    ultima_manutencao = Column(Date)
    ultima_afericao_deltap = Column(Float)
    quantidade_mangas = Column(Integer)
    material_manga = Column(String(100))

class LogFiltro(Base):
    __tablename__ = 'logs_filtros'
    id = Column(Integer, primary_key=True)
    filtro_id = Column(Integer)
    valor_deltap = Column(Float)
    status_anterior = Column(String(50))
    status_novo = Column(String(50))
    data_evento = Column(DateTime, default=datetime.now)

engine = create_engine('mysql+mysqlconnector://root:23245623@localhost:3306/filtros')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

def processar_filtro(id_fornecido, status_fornecido):
    # 1. Busca no banco se já existe um filtro com esse ID
    filtro_existente = session.query(Filtro).filter_by(id=id_fornecido).first()

    if filtro_existente:
        print(f"O filtro {id_fornecido} já consta no sistema.")
        return filtro_existente
    else:
        novo_filtro = Filtro(id=id_fornecido, status=status_fornecido)
        
        session.add(novo_filtro)
        session.commit()
        
        print(f"Filtro {id_fornecido} cadastrado com sucesso!")
        return novo_filtro

def analise_deltap(id_filtro):
    
    LIMITE_ATENCAO = 100.2 #mmH2O
    LIMITE_CRITICO = 60.8 #mmH2O
    
    filtro = session.query(Filtro).filter_by(id=id_filtro).first()

    if not filtro:
        print(f"Filtro {id_filtro} não encontrado!")
        return None
    
    valor_atual = filtro.ultima_afericao_deltap

    if valor_atual >= LIMITE_ATENCAO:
        filtro.status = 'ATENÇÃO'
        print(f"O Filtro {id_filtro} atingiu o limite de atenção.")    
    elif valor_atual <= LIMITE_CRITICO:
        filtro.status = 'CRÍTICO'
        print(f"O Filtro {id_filtro} atingiu o limite crítico. Substituição imediata necessária.")   
    else:
        filtro.status = 'OPERACIONAL'
        print(f"O Filtro {id_filtro} está operando dentro dos parâmetros normais.")
        filtro.status = 'OPERACIONAL'
    
    session.commit()
    return valor_atual


def verificar_cronograma_manutencao(dias_limite=120):
    data_limite = datetime.now().date() - timedelta(days=dias_limite)
    filtros_atrasados = session.query(Filtro).filter(Filtro.ultima_manutencao < data_limite).all()

    if filtros_atrasados:
        print("Filtros com manutenção em atraso: {dias_limite} dias")
        for f in filtros_atrasados:
            print(f"Filtro ID: {f.id}, Última Manutenção: {f.ultima_manutencao}")
        else: 
            print("Nenhum filtro com manutenção em atraso.")
    return filtros_atrasados

def validar_leitura(valor):
    if valor < 0 or valor > 1000:
        print(f" Leitura inválida: {valor} póssivel erro de leitura.")
        return False
    return True

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/analisar/<int:id_filtro>', methods=['GET'])
def analisar_filtro(id_filtro):
    valor = analise_deltap(id_filtro)

    filtro = session.query(Filtro).filter_by(id=id_filtro).first()
    if filtro:
        return jsonify({
            'id': filtro.id,
            'status': filtro.status,
            'deltap': filtro.ultima_afericao_deltap,
            'mensagem': f'ánalise concluida, valor atual de deltap: {valor} mmH2O',
        })
    return jsonify({'mensagem': 'Filtro não encontrado'}), 404

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_filtro():
    dados = request.json
    try:
        novo_filtro = Filtro(
            id=int(dados['id']),
            status=dados.get('status'),
            quantidade_mangas=dados.get('quantidade_mangas', 0),
            material_manga=dados.get('material_manga', 'Não definido'),
            ultima_manutencao=datetime.now().date(),
            ultima_afericao_deltap= 0.0
        )
        session.add(novo_filtro)
        session.commit()
        return jsonify({"mensagem": f"Filtro {dados['id']} cadastrado com sucesso!"}), 201
    except Exception as e:
        session.rollback()
        return jsonify({"mensagem": "Erro ao cadastrar filtro", "erro": str(e)}), 400
        
@app.route('/api/atualizar', methods=['POST'])
def atualizar_filtro():
    dados = request.json
    filtro_alvo = session.query(Filtro).filter_by(id=dados['id']).first()

    if not filtro_alvo:
        return jsonify({'erro': 'Filtro não encontrado'}), 404
    
    try:
        if 'deltap' in dados:
            filtro_alvo.ultima_afericao_deltap = float(dados['deltap'])

        if dados.get('manutencao'):
            filtro_alvo.ultima_manutencao = datetime.strptime(dados['manutencao'], '%Y-%m-%d').date()
        
        session.commit()

        analise_deltap(filtro_alvo.id)

        return jsonify({'mensagem': 'Dados atualizados e status reavaliado com sucesso!'})
    except Exception as e:
        session.rollback()
        return jsonify({'erro': str(e)}), 400

@app.route('/api/historico/',methods=['GET'])
def listar_filtros():
    filtros = session.query(Filtro).all()
    lista_filtros = []
    for f in filtros:
        lista_filtros.append({
            'id': f.id,
            'status': f.status,
            'ultima_manutencao': str(f.ultima_manutencao),
            'deltap': f.ultima_afericao_deltap
        })
    return jsonify(lista_filtros)

if __name__ == '__main__':
    app.run(debug=True)
