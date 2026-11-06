import pytest
from sqlalchemy import func, inspect
from sqlalchemy.exc import OperationalError

from sigetec import create_app
from sigetec.models import Usuario, db


@pytest.fixture
def empty_app():
    # Sem tabelas e sem referência a qualquer configuração do banco hospedado.
    app = create_app({
        'TESTING': True, 'APP_ENV': 'development',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'chave-apenas-dos-testes-isolados',
        'INIT_DB_ON_START': False, 'CREATE_ADMIN_ON_START': False,
        'BOOTSTRAP_ADMIN_NAME': None, 'BOOTSTRAP_ADMIN_EMAIL': None,
        'BOOTSTRAP_ADMIN_PASSWORD': None,
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


def configure_admin(app, **overrides):
    app.config.update(
        INIT_DB_ON_START=True, CREATE_ADMIN_ON_START=True,
        BOOTSTRAP_ADMIN_NAME='Administrador Teste',
        BOOTSTRAP_ADMIN_EMAIL='ADMIN@example.com',
        BOOTSTRAP_ADMIN_PASSWORD='Senha-apenas-teste-123',
    )
    app.config.update(overrides)


def test_padrao_nao_cria_tabelas_nem_conecta(empty_app, monkeypatch):
    with empty_app.app_context():
        engine = db.engine
        def fail(*args, **kwargs):
            pytest.fail('Com as flags desativadas, não deve abrir conexão.')
        monkeypatch.setattr(engine, 'begin', fail)
        result = empty_app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code == 0
    assert 'desativada' in result.output


def test_somente_tabelas(empty_app):
    empty_app.config['INIT_DB_ON_START'] = True
    runner = empty_app.test_cli_runner()
    assert runner.invoke(args=['inicializar-deploy']).exit_code == 0
    assert runner.invoke(args=['inicializar-deploy']).exit_code == 0
    with empty_app.app_context():
        assert set(inspect(db.engine).get_table_names()) == {'usuarios', 'chamados', 'comentarios'}
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 0


def test_tabelas_e_primeiro_admin_idempotente(empty_app):
    configure_admin(empty_app)
    runner = empty_app.test_cli_runner()
    result = runner.invoke(args=['inicializar-deploy'])
    assert result.exit_code == 0, result.output
    assert 'Administrador criado.' in result.output
    assert 'Senha-apenas-teste-123' not in result.output
    with empty_app.app_context():
        usuario = db.session.scalar(db.select(Usuario))
        assert usuario.email == 'admin@example.com' and usuario.perfil == 'administrador'
        assert usuario.ativo and usuario.verificar_senha('Senha-apenas-teste-123')
        original_hash = usuario.senha_hash
    empty_app.config['BOOTSTRAP_ADMIN_PASSWORD'] = 'Outra-senha-teste-123'
    assert runner.invoke(args=['inicializar-deploy']).exit_code == 0
    with empty_app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 1
        assert db.session.scalar(db.select(Usuario)).senha_hash == original_hash


@pytest.mark.parametrize('overrides', [
    {'BOOTSTRAP_ADMIN_PASSWORD': None}, {'BOOTSTRAP_ADMIN_PASSWORD': 'curta'},
    {'BOOTSTRAP_ADMIN_EMAIL': 'invalido'}, {'BOOTSTRAP_ADMIN_EMAIL': None},
    {'BOOTSTRAP_ADMIN_NAME': ''}, {'BOOTSTRAP_ADMIN_NAME': 'a' * 121},
])
def test_dados_invalidos_impedem_ddl(empty_app, overrides):
    configure_admin(empty_app, **overrides)
    result = empty_app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code != 0
    with empty_app.app_context():
        assert inspect(db.engine).get_table_names() == []


def test_admin_sem_ativar_criacao_de_tabelas(empty_app):
    configure_admin(empty_app, INIT_DB_ON_START=False)
    result = empty_app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code != 0
    assert 'Banco sem tabelas' in result.output
    with empty_app.app_context():
        assert inspect(db.engine).get_table_names() == []


def test_conflito_de_estrutura_preserva_dados(empty_app):
    configure_admin(empty_app)
    with empty_app.app_context():
        with db.engine.begin() as connection:
            connection.exec_driver_sql('CREATE TABLE usuarios (id INTEGER PRIMARY KEY, preservado TEXT)')
            connection.exec_driver_sql("INSERT INTO usuarios (preservado) VALUES ('dado-existente')")
    result = empty_app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code != 0
    with empty_app.app_context():
        with db.engine.connect() as connection:
            assert connection.exec_driver_sql('SELECT preservado FROM usuarios').scalar_one() == 'dado-existente'
            assert set(inspect(connection).get_table_names()) == {'usuarios'}


def test_nao_promove_usuario_com_email_conflitante(app):
    with app.app_context():
        usuario = Usuario(nome='Solicitante', email='admin@example.com', perfil='solicitante', ativo=True)
        usuario.definir_senha('Senha-original-teste-123')
        db.session.add(usuario)
        db.session.commit()
    configure_admin(app)
    result = app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code != 0
    with app.app_context():
        usuario = db.session.scalar(db.select(Usuario))
        assert usuario.perfil == 'solicitante'
        assert usuario.verificar_senha('Senha-original-teste-123')


def test_nao_reativa_administrador(app):
    with app.app_context():
        usuario = Usuario(nome='Anterior', email='anterior@example.com', perfil='administrador', ativo=False)
        usuario.definir_senha('Senha-original-teste-123')
        db.session.add(usuario)
        db.session.commit()
    configure_admin(app)
    assert app.test_cli_runner().invoke(args=['inicializar-deploy']).exit_code == 0
    with app.app_context():
        usuario = db.session.scalar(db.select(Usuario))
        assert not usuario.ativo and usuario.email == 'anterior@example.com'
        assert usuario.verificar_senha('Senha-original-teste-123')


def test_falha_banco_omite_segredos(empty_app, monkeypatch):
    configure_admin(empty_app)
    with empty_app.app_context():
        def fail(*args, **kwargs):
            raise OperationalError('sql-secreto', {}, Exception('credencial-super-secreta'))
        monkeypatch.setattr(db.engine, 'begin', fail)
        result = empty_app.test_cli_runner().invoke(args=['inicializar-deploy'])
    assert result.exit_code != 0
    assert 'credencial-super-secreta' not in result.output
    assert 'Senha-apenas-teste-123' not in result.output
    assert 'detalhes privados foram omitidos' in result.output


def test_cli_admin_oculto_independente_da_demonstracao(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['criar-admin'], input='Administrador\nadmin@example.com\nSenha-admin-teste-123\nSenha-admin-teste-123\n')
    assert result.exit_code == 0, result.output
    assert 'Senha-admin-teste-123' not in result.output
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 1
        assert db.session.scalar(db.select(Usuario)).perfil == 'administrador'
    again = runner.invoke(args=['criar-admin'], input='Outro\noutro@example.com\nOutra-senha-teste-123\nOutra-senha-teste-123\n')
    assert again.exit_code == 0
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 1
