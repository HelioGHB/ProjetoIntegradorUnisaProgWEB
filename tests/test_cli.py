from sqlalchemy import func

from sigetec import create_app
from sigetec.models import Usuario, db


def test_demo_sem_senha_fixa_e_sem_sobrescrita(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=['preparar-demo'], input='Senha-escolhida-12345\nSenha-escolhida-12345\n')
    assert result.exit_code == 0, result.output
    assert 'Senha-escolhida-12345' not in result.output
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 3
        admin = db.session.scalar(db.select(Usuario).where(Usuario.perfil == 'administrador'))
        assert admin.verificar_senha('Senha-escolhida-12345')
    assert runner.invoke(args=['preparar-demo']).exit_code != 0
    assert runner.invoke(args=['init-db']).exit_code == 0


def test_senha_invalida_nao_cria_contas(app):
    result = app.test_cli_runner().invoke(args=['preparar-demo'], input='curta\ncurta\n')
    assert result.exit_code != 0
    with app.app_context():
        assert db.session.scalar(db.select(func.count()).select_from(Usuario)) == 0


def test_estrutura_antiga_e_preservada():
    app = create_app({'TESTING': True, 'APP_ENV': 'development', 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        with db.engine.begin() as conn:
            conn.exec_driver_sql('CREATE TABLE usuarios (id INTEGER PRIMARY KEY, preservado TEXT)')
            conn.exec_driver_sql("INSERT INTO usuarios (preservado) VALUES ('dado-existente')")
        result = app.test_cli_runner().invoke(args=['init-db'])
        assert result.exit_code != 0
        assert 'nenhum dado foi alterado' in result.output
        with db.engine.connect() as conn:
            assert conn.exec_driver_sql('SELECT preservado FROM usuarios').scalar_one() == 'dado-existente'
        db.engine.dispose()
