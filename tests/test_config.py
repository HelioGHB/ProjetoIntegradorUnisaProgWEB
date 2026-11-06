import pytest

from config import Config
from sigetec import create_app
from sigetec.models import db


def production(**overrides):
    config = {'TESTING': True, 'APP_ENV': 'production', 'SECRET_KEY': 'chave-de-testes-isolados-com-32-caracteres',
              'SQLALCHEMY_DATABASE_URI': 'postgresql://app:exemplo@localhost/teste',
              'TRUSTED_HOSTS': ['sigetec.example.com'], 'SESSION_COOKIE_SECURE': True}
    config.update(overrides)
    return config


def test_local_nao_usa_postgres_antigo(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'development')
    monkeypatch.setenv('DATABASE_URL', 'postgresql://app:exemplo@localhost/antigo')
    assert Config().SQLALCHEMY_DATABASE_URI == 'sqlite:///sigetec.sqlite3'


@pytest.mark.parametrize('config', [{'SECRET_KEY': None}, {'SECRET_KEY': 'curta'}, {'SQLALCHEMY_DATABASE_URI': None},
                                    {'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:exemplo@localhost/teste'},
                                    {'SQLALCHEMY_DATABASE_URI': 'postgresql://app:exemplo@localhost/teste?sslmode=disable'},
                                    {'DEBUG': True}, {'SESSION_COOKIE_SECURE': False}])
def test_producao_recusa_configuracao_insegura(config):
    with pytest.raises(ValueError):
        create_app(production(**config))


def test_producao_driver_tls_host_e_proxy():
    from flask import request
    app = create_app(production())
    @app.get('/teste-proxy')
    def teste_proxy():
        return {'protocolo': request.scheme, 'host': request.host}
    with app.app_context():
        assert db.engine.url.drivername == 'postgresql+psycopg'
        assert db.engine.url.query['sslmode'] == 'require'
        db.engine.dispose()
    client = app.test_client()
    page = client.get('/teste-proxy', base_url='http://sigetec.example.com', headers={'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': 'forjado.example.com'})
    assert page.json == {'protocolo': 'https', 'host': 'sigetec.example.com'}
    assert page.headers['Strict-Transport-Security'] == 'max-age=31536000'
    assert client.get('/', base_url='https://outro.example.com').status_code == 400
