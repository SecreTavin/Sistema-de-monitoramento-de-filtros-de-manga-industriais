from app.models import session as db_session, Filtro

#Calculo de análise Delta P
def analise_deltap(id_filtro):
    LIMITE_ATENCAO_ALTO = 100.2 #mmH2O
    LIMITE_ATENCAO_BAIXO = 60.8 #mmH2O
    LIMITE_CRITICO_BAIXO = 50.1 #mmH2O
    LIMITE_CRITICO_ALTO = 200.1 #mmH2O


    
    filtro = db_session.query(Filtro).filter_by(id=id_filtro).first()

    if not filtro:
        return None
    
    valor_atual = filtro.ultima_afericao_deltap

    if valor_atual <= LIMITE_ATENCAO_BAIXO or valor_atual >= LIMITE_ATENCAO_ALTO:
        filtro.status = 'ATENÇÃO'
    elif valor_atual <= LIMITE_CRITICO_BAIXO or valor_atual >= LIMITE_CRITICO_ALTO:
        filtro.status = 'CRÍTICO'
    else:
        filtro.status = 'OPERACIONAL'
    
    db_session.commit()
    return valor_atual
