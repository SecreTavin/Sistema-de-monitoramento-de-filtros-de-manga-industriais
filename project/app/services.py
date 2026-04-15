from app.models import session, Filtro

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
