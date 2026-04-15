from flask import render_template, jsonify, request
from datetime import datetime
from app.models import session, Filtro
from app.services import analise_deltap

def init_routes(app):
    
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
                'observacoes': filtro.observacoes,
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
                return jsonify({"erro": f"Operação negada: O ativo com ID {id_filtro} já está cadastrado."}), 409
                
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
            if 'deltap' in dados and dados['deltap'] != '':
                filtro_alvo.ultima_afericao_deltap = float(dados['deltap'])

            if dados.get('manutencao'):
                filtro_alvo.ultima_manutencao = datetime.strptime(dados['manutencao'], '%Y-%m-%d').date()
                
            if 'observacoes' in dados and dados['observacoes'].strip() != '':
                filtro_alvo.observacoes = dados['observacoes']
            
            session.commit()
            analise_deltap(filtro_alvo.id) 

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
                'observacoes': f.observacoes
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