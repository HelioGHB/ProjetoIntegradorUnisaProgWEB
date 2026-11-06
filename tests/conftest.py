import re

import pytest

from sigetec import create_app
from sigetec.models import Chamado, Usuario, db


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True, 'APP_ENV': 'development',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'chave-apenas-dos-testes-em-memoria',
        'SESSION_COOKIE_SECURE': False,
    })
    assert app.test_cli_runner().invoke(args=['init-db']).exit_code == 0
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuarios(app):
    ids = {}
    with app.app_context():
        for nome, perfil in [('admin', 'administrador'), ('tecnico', 'tecnico'), ('solicitante', 'solicitante'), ('outro', 'solicitante'), ('outrotecnico', 'tecnico'), ('inativo', 'solicitante')]:
            usuario = Usuario(nome=nome, email=f'{nome}@example.com', perfil=perfil, ativo=nome != 'inativo')
            usuario.definir_senha('Senha-apenas-teste-123')
            db.session.add(usuario)
            db.session.flush()
            ids[nome] = usuario.id
        db.session.commit()
    return ids


@pytest.fixture
def chamado_id(app, usuarios):
    with app.app_context():
        chamado = Chamado(titulo='Sem acesso à rede', descricao='Computador sem conexão.', prioridade='alta', solicitante_id=usuarios['solicitante'])
        db.session.add(chamado)
        db.session.commit()
        return chamado.id


def csrf(client, path='/login'):
    response = client.get(path)
    assert response.status_code == 200
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.text)
    assert match
    return match.group(1)


def entrar(client, nome='solicitante', senha='Senha-apenas-teste-123'):
    return client.post('/login', data={'email': f'{nome}@example.com', 'senha': senha, 'csrf_token': csrf(client)})


def enviar(client, path, dados, pagina):
    return client.post(path, data={**dados, 'csrf_token': csrf(client, pagina)})
