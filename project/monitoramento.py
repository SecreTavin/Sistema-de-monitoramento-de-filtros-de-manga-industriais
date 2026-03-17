from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

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

# Configuração do banco de dados
db_uri = os.getenv('DATABASE_URI')

if not db_uri:
    raise ValueError("⚠️ ERRO CRÍTICO: Variável DATABASE_URI não encontrada. Verifique se o ficheiro .env existe.")

engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)
session = Session()

# Cria as tabelas se não existirem
Base.metadata.create_all(engine)

#Calculo de análise Delta P
def analise_deltap(id_filtro):
    LIMITE_ATENCAO = 100.2 #mmH2O
    LIMITE_CRITICO = 60.8 #mmH2O
    
    filtro = session.query(Filtro).filter_by(id=id_filtro).first()

    if not filtro:
        return None
    
    valor_atual = filtro.ultima_afericao_deltap

    if valor_atual >= LIMITE_ATENCAO:
        filtro.status = 'ATENÇÃO'
    elif valor_atual <= LIMITE_CRITICO:
        filtro.status = 'CRÍTICO'
    else:
        filtro.status = 'OPERACIONAL'
    
    session.commit()
    return valor_atual

# --- ROTAS DA API ---
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
            'observacoes': filtro.observacoes, # Incluindo a nova variável no payload
            'mensagem': f'Análise concluída. Valor atual de Delta P: {valor} mmH2O',
        })
    return jsonify({'mensagem': 'Filtro não encontrado'}), 404

@app.route('/api/cadastrar', methods=['POST'])
def cadastrar_filtro():
    dados = request.json
    try:
        id_filtro = int(dados['id'])

        filtro_existente = session.query(Filtro).filter_by(id=id_filtro).first()
            
        if filtro_existente:
            return jsonify({"erro": f"Operação negada: O ativo com ID {id_filtro} já está cadastrado no sistema."}), 409
                
        novo_filtro = Filtro(
            id=id_filtro,
            status=dados.get('status', 'OPERACIONAL'),
            quantidade_mangas=dados.get('quantidade_mangas', 0),
            material_manga=dados.get('material_manga', 'Não definido'),
            ultima_manutencao=datetime.now().date(),
            ultima_afericao_deltap= 0.0,
            observacoes="Ativo recém-cadastrado. Nenhuma avaria reportada."
        )
        session.add(novo_filtro)
        session.commit()
        return jsonify({"mensagem": f"Filtro {id_filtro} cadastrado com sucesso!"}), 201
            
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
        # Atualiza Delta P
        if 'deltap' in dados and dados['deltap'] != '':
            filtro_alvo.ultima_afericao_deltap = float(dados['deltap'])

        # Atualiza Data de Manutenção
        if dados.get('manutencao'):
            filtro_alvo.ultima_manutencao = datetime.strptime(dados['manutencao'], '%Y-%m-%d').date()
            
        #Atualiza o Relatório de Avarias (String)
        if 'observacoes' in dados and dados['observacoes'].strip() != '':
            filtro_alvo.observacoes = dados['observacoes']
        
        session.commit()
        analise_deltap(filtro_alvo.id) # Reavalia o status com a nova pressão

        return jsonify({'mensagem': 'Dados de inspeção atualizados com sucesso!'})
    except Exception as e:
        session.rollback()
        return jsonify({'erro': str(e)}), 400

@app.route('/api/historico/', methods=['GET'])
def listar_filtros():
    filtros = session.query(Filtro).all()
    lista_filtros = []
    for f in filtros:
        lista_filtros.append({
            'id': f.id,
            'status': f.status,
            'ultima_manutencao': str(f.ultima_manutencao),
            'deltap': f.ultima_afericao_deltap,
            'observacoes': f.observacoes # Retornando para a tabela do front
        })
    return jsonify(lista_filtros)

@app.route('/api/excluir/<int:id_filtro>', methods=['DELETE'])
def excluir_filtro(id_filtro):
    filtro_alvo = session.query(Filtro).filter_by(id=id_filtro).first()

    if not filtro_alvo:
        return jsonify({'erro': 'Operação falhou: Filtro não encontrado no banco de dados.'}), 404
    
    try:
        session.delete(filtro_alvo)
        session.commit()
        return jsonify({'mensagem': f'Filtro {id_filtro} removido do sistema com sucesso!'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'erro': f'Erro interno ao tentar excluir: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
