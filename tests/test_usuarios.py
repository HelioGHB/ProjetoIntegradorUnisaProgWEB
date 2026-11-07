import pytest
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from conftest import entrar, enviar
from sigetec.models import Chamado, Usuario, db


def dados(**overrides):
    result = {'nome': 'Nova Pessoa', 'email': 'nova@example.com', 'perfil': 'solicitante',
              'senha': 'Senha-inicial-teste-123', 'confirmar_senha': 'Senha-inicial-teste-123'}
    result.update(overrides)
    return result


def test_paginas_exigem_login(client):
    assert client.get('/usuarios').status_code == 302
    assert client.get('/usuarios/novo').status_code == 302


@pytest.mark.parametrize('perfil', ['tecnico', 'solicitante'])
def test_somente_administrador_gerencia(client, usuarios, perfil):
    entrar(client, perfil)
    assert client.get('/usuarios').status_code == 403
    assert client.get('/usuarios/novo').status_code == 403
    assert enviar(client, '/usuarios/novo', dados(), '/chamados').status_code == 403
    assert enviar(client, f"/usuarios/{usuarios['outro']}/desativar", {}, '/chamados').status_code == 403


@pytest.mark.parametrize('perfil', ['tecnico', 'solicitante'])
def test_cadastro_com_hash_e_login(app, client, usuarios, perfil):
    entrar(client, 'admin')
    assert client.get('/usuarios').status_code == 200
    assert 'Cadastrar usuário' in client.get('/usuarios').text
    result = enviar(client, '/usuarios/novo', dados(email=' NOVA@example.com ', perfil=perfil), '/usuarios/novo')
    assert result.location == '/usuarios'
    with app.app_context():
        usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == 'nova@example.com'))
        assert usuario.nome == 'Nova Pessoa' and usuario.perfil == perfil and usuario.ativo
        assert usuario.senha_hash != 'Senha-inicial-teste-123'
        assert usuario.verificar_senha('Senha-inicial-teste-123')
    outro_client = app.test_client()
    assert entrar(outro_client, 'nova', 'Senha-inicial-teste-123').location == '/chamados'
    assert 'Usuários</a>' not in outro_client.get('/chamados').text


def test_duplicidade_preserva_conta(app, client, usuarios):
    entrar(client, 'admin')
    result = enviar(client, '/usuarios/novo', dados(email=' SOLICITANTE@example.com '), '/usuarios/novo')
    assert 'Já existe um usuário' in result.text
    assert 'Senha-inicial-teste-123' not in result.text
    with app.app_context():
        usuario = db.session.get(Usuario, usuarios['solicitante'])
        assert usuario.verificar_senha('Senha-apenas-teste-123')
        assert usuario.nome == 'solicitante'


@pytest.mark.parametrize('overrides', [
    {'perfil': 'administrador'}, {'perfil': 'root'}, {'nome': '   '},
    {'email': 'invalido'}, {'senha': 'curta', 'confirmar_senha': 'curta'},
    {'confirmar_senha': 'senha-diferente'},
])
def test_validacao_recusa_cadastro(app, client, usuarios, overrides):
    entrar(client, 'admin')
    with app.app_context():
        anterior = db.session.scalar(db.select(func.count()).select_from(Usuario))
    result = enviar(client, '/usuarios/novo', dados(**overrides), '/usuarios/novo')
    assert result.status_code == 200
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == anterior


def test_ativacao_idempotente_preserva_dados(app, client, usuarios, chamado_id):
    entrar(client, 'admin')
    path = f"/usuarios/{usuarios['solicitante']}/desativar"
    assert client.get(path).status_code == 405
    assert enviar(client, path, {}, '/usuarios').status_code == 302
    assert enviar(client, path, {}, '/usuarios').status_code == 302
    with app.app_context():
        assert not db.session.get(Usuario, usuarios['solicitante']).ativo
        assert db.session.get(Chamado, chamado_id).solicitante_id == usuarios['solicitante']
    solicitante = app.test_client()
    assert entrar(solicitante).status_code == 200
    assert solicitante.get('/chamados').status_code == 302
    assert enviar(client, f"/usuarios/{usuarios['solicitante']}/ativar", {}, '/usuarios').status_code == 302
    assert entrar(solicitante).location == '/chamados'


def test_desativacao_revoga_sessao_em_uso(app, client, usuarios):
    solicitante = app.test_client()
    entrar(solicitante)
    entrar(client, 'admin')
    enviar(client, f"/usuarios/{usuarios['solicitante']}/desativar", {}, '/usuarios')
    assert solicitante.get('/chamados').status_code == 302


def test_conta_admin_nao_pode_ser_bloqueada(app, client, usuarios):
    entrar(client, 'admin')
    assert enviar(client, f"/usuarios/{usuarios['admin']}/desativar", {}, '/usuarios').status_code == 403
    with app.app_context():
        assert db.session.get(Usuario, usuarios['admin']).ativo


def test_csrf_cadastro_e_alteracao(client, usuarios):
    entrar(client, 'admin')
    assert client.post('/usuarios/novo', data=dados()).status_code == 400
    assert client.post(f"/usuarios/{usuarios['solicitante']}/desativar").status_code == 400


def test_falha_de_integridade_nao_expoe_detalhes(app, client, usuarios, monkeypatch):
    entrar(client, 'admin')
    def fail(*args, **kwargs):
        raise IntegrityError('sql', {}, Exception('detalhe-privado'))
    monkeypatch.setattr(db.session, 'commit', fail)
    result = enviar(client, '/usuarios/novo', dados(), '/usuarios/novo')
    assert result.status_code == 200
    assert 'Não foi possível cadastrar' in result.text
    assert 'detalhe-privado' not in result.text
    assert 'Senha-inicial-teste-123' not in result.text


def test_id_inexistente_e_acao_invalida(client, usuarios):
    entrar(client, 'admin')
    assert enviar(client, '/usuarios/999999/desativar', {}, '/usuarios').status_code == 404
    assert enviar(client, f"/usuarios/{usuarios['solicitante']}/apagar", {}, '/usuarios').status_code == 404
