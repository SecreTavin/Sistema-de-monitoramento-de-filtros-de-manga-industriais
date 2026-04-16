from app.models import session, Usuario

def criar_usuario(username, password):
    if session.query(Usuario).filter_by(username=username).first():
        print(f"Usuário '{username}' já existe.")
        return
    
    novo_usuario = Usuario(username=username)
    novo_usuario.set_password(password)

    session.add(novo_usuario)
    session.commit()
    print(f"Usuário '{username}' criado com sucesso!")

if __name__ == "__main__":
    criar_usuario("admin_octavio", "admin123")
    