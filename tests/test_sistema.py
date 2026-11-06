import pytest
from sqlalchemy import func, insert
from sqlalchemy.exc import IntegrityError, OperationalError

from conftest import entrar, enviar, csrf
from sigetec.models import Chamado, Comentario, Usuario, db


def test_inicio_sem_cdn(client):
    page = client.get('/')
    assert page.status_code == 200
    assert 'cdn.jsdelivr.net' not in page.text


def test_login_e_logout(client, usuarios):
    assert entrar(client).location == '/chamados'
    assert client.get('/chamados').status_code == 200
    assert client.get('/logout').status_code == 405
    response = enviar(client, '/logout', {}, '/chamados')
    assert response.location == '/login'
    assert client.get('/chamados').status_code == 302


@pytest.mark.parametrize('nome,senha', [('solicitante', 'errada'), ('inativo', 'Senha-apenas-teste-123'), ('ausente', 'Senha-apenas-teste-123')])
def test_login_invalido_generico(client, usuarios, nome, senha):
    response = entrar(client, nome, senha)
    assert 'E-mail ou senha inválidos.' in response.text
    assert client.get('/chamados').status_code == 302


def test_acesso_anonimo(client):
    assert client.get('/chamados').status_code == 302
    assert client.get('/chamados/novo').status_code == 302
    assert client.get('/chamados/1').status_code == 302


def test_csrf_login_e_mutacoes(client, usuarios):
    assert client.post('/login', data={'email': 'solicitante@example.com', 'senha': 'Senha-apenas-teste-123'}).status_code == 400
    entrar(client)
    assert client.post('/chamados/novo', data={'titulo': 'Teste', 'descricao': 'Teste', 'prioridade': 'alta'}).status_code == 400
    assert client.post('/logout').status_code == 400


def test_abertura_e_validacao(client, usuarios, app):
    entrar(client)
    response = enviar(client, '/chamados/novo', {'titulo': 'Rede', 'descricao': 'Sem conexão', 'prioridade': 'alta'}, '/chamados/novo')
    assert response.status_code == 302
    assert 'Rede' in client.get(response.location).text
    response = enviar(client, '/chamados/novo', {'titulo': '   ', 'descricao': 'Teste', 'prioridade': 'urgente'}, '/chamados/novo')
    assert response.status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Chamado)) == 1


@pytest.mark.parametrize('nome', ['admin', 'tecnico'])
def test_apenas_solicitante_abre(client, usuarios, nome):
    entrar(client, nome)
    assert client.get('/chamados/novo').status_code == 403


@pytest.mark.parametrize('nome', ['outro', 'tecnico', 'outrotecnico'])
def test_privacidade_lista_e_detalhe(client, chamado_id, nome):
    entrar(client, nome)
    assert 'Sem acesso à rede' not in client.get('/chamados').text
    assert client.get(f'/chamados/{chamado_id}').status_code == 403
    response = enviar(client, f'/chamados/{chamado_id}/comentar', {'conteudo': 'Não permitido'}, '/chamados')
    assert response.status_code == 403


def test_fluxo_completo(app, usuarios, chamado_id):
    admin, tecnico, solicitante = (app.test_client() for _ in range(3))
    detalhe = f'/chamados/{chamado_id}'
    entrar(admin, 'admin')
    assert admin.get(detalhe).status_code == 200
    assert enviar(admin, detalhe + '/atribuir', {'tecnico_id': usuarios['tecnico']}, detalhe).status_code == 302
    entrar(tecnico, 'tecnico')
    assert 'Sem acesso à rede' in tecnico.get('/chamados').text
    assert enviar(tecnico, detalhe + '/status', {'status': 'em_andamento'}, detalhe).status_code == 302
    assert enviar(tecnico, detalhe + '/comentar', {'conteudo': 'Cabo substituído; conexão restabelecida.'}, detalhe).status_code == 302
    assert enviar(tecnico, detalhe + '/status', {'status': 'resolvido'}, detalhe).status_code == 302
    entrar(solicitante)
    page = solicitante.get(detalhe).text
    assert 'resolvido' in page and 'Cabo substituído' in page
    assert enviar(solicitante, detalhe + '/comentar', {'conteudo': 'Funcionando, obrigado.'}, detalhe).status_code == 302
    assert enviar(admin, detalhe + '/status', {'status': 'fechado'}, detalhe).status_code == 302
    assert enviar(tecnico, detalhe + '/status', {'status': 'aberto'}, detalhe).status_code == 403
    assert enviar(admin, detalhe + '/status', {'status': 'aberto'}, detalhe).status_code == 302
    with app.app_context():
        assert db.session.get(Chamado, chamado_id).status == 'aberto'
        assert db.session.scalar(db.select(func.count()).select_from(Comentario)) == 2


def test_solicitante_nao_atribui_nem_atualiza(client, usuarios, chamado_id):
    entrar(client)
    detalhe = f'/chamados/{chamado_id}'
    assert enviar(client, detalhe + '/atribuir', {'tecnico_id': usuarios['tecnico']}, detalhe).status_code == 403
    assert enviar(client, detalhe + '/status', {'status': 'fechado'}, detalhe).status_code == 403


def test_atribuicao_recusa_usuario_que_nao_e_tecnico(app, client, usuarios, chamado_id):
    entrar(client, 'admin')
    detalhe = f'/chamados/{chamado_id}'
    assert enviar(client, detalhe + '/atribuir', {'tecnico_id': usuarios['solicitante']}, detalhe).status_code == 302
    with app.app_context():
        assert db.session.get(Chamado, chamado_id).tecnico_id is None


def test_tecnico_nao_pode_atribuir(client, usuarios, chamado_id):
    entrar(client, 'tecnico')
    assert enviar(client, f'/chamados/{chamado_id}/atribuir', {'tecnico_id': usuarios['tecnico']}, '/chamados').status_code == 403


def test_status_invalido_nao_persiste(app, client, chamado_id):
    entrar(client, 'admin')
    detalhe = f'/chamados/{chamado_id}'
    enviar(client, detalhe + '/status', {'status': 'invalido'}, detalhe)
    with app.app_context():
        assert db.session.get(Chamado, chamado_id).status == 'aberto'


def test_conteudo_html_escapado(client, usuarios):
    entrar(client)
    response = enviar(client, '/chamados/novo', {'titulo': '<script>alert(1)</script>', 'descricao': '<img src=x onerror=alert(1)>', 'prioridade': 'media'}, '/chamados/novo')
    page = client.get(response.location).text
    assert '<script>alert(1)</script>' not in page
    assert '&lt;script&gt;' in page
    assert '<img src=x' not in page


def test_hash_e_email_duplicado(app, usuarios):
    with app.app_context():
        usuario = db.session.get(Usuario, usuarios['solicitante'])
        assert usuario.verificar_senha('Senha-apenas-teste-123')
        assert usuario.senha_hash != 'Senha-apenas-teste-123'
        db.session.add(Usuario(nome='Outro', email=usuario.email, perfil='tecnico', senha_hash='apenas-teste'))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_integridade_de_chamado(app, usuarios):
    with app.app_context():
        with pytest.raises(IntegrityError):
            db.session.execute(insert(Chamado).values(titulo='Teste', descricao='Teste', prioridade='alta', status='aberto', solicitante_id=99999))
            db.session.commit()
        db.session.rollback()
        with pytest.raises(IntegrityError):
            db.session.execute(insert(Chamado).values(titulo='Teste', descricao='Teste', prioridade='urgente', status='aberto', solicitante_id=usuarios['solicitante']))
            db.session.commit()
        db.session.rollback()


def test_desativacao_revoga_sessao(app, client, usuarios):
    entrar(client)
    with app.app_context():
        db.session.get(Usuario, usuarios['solicitante']).ativo = False
        db.session.commit()
    assert client.get('/chamados').status_code == 302


def test_falha_banco_nao_expoe_excecao(client, monkeypatch):
    def fail(*args, **kwargs):
        raise OperationalError('sql', {}, Exception('segredo-interno'))
    monkeypatch.setattr(db.session, 'execute', fail)
    response = client.get('/healthz')
    assert response.status_code == 503
    assert 'segredo-interno' not in response.text


def test_healthz_e_nao_encontrado(client, usuarios):
    assert client.get('/healthz').json == {'status': 'ok'}
    entrar(client)
    assert client.get('/chamados/9999').status_code == 404
