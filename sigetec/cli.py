"""Inicialização explícita, sem apagar ou recriar banco existente."""
import click
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from sigetec.models import Usuario, db


def inicializar_banco():
    inspector = inspect(db.engine)
    existentes = set(inspector.get_table_names())
    esperadas = set(db.metadata.tables)
    if existentes:
        estrutura_igual = existentes == esperadas and all(
            {coluna['name'] for coluna in inspector.get_columns(nome)}
            == set(db.metadata.tables[nome].columns.keys()) for nome in esperadas
        )
        if not estrutura_igual:
            raise click.ClickException('O banco já contém outra estrutura. Use um banco novo; nenhum dado foi alterado.')
        return False
    db.create_all()
    return True


def register_cli(app):
    @app.cli.command('init-db')
    def init_db():
        """Cria as três tabelas apenas se o banco estiver vazio."""
        try:
            criado = inicializar_banco()
        except SQLAlchemyError:
            raise click.ClickException('Não foi possível inicializar o banco. Confira a configuração.') from None
        click.echo('Banco inicializado.' if criado else 'Banco já inicializado; nenhuma alteração realizada.')

    @app.cli.command('preparar-demo')
    def preparar_demo():
        """Prepara o banco e três contas fictícias com senha escolhida no terminal."""
        if app.config['APP_ENV'] == 'production' and not app.config.get('DEMO_MODE'):
            raise click.ClickException('Em produção, habilite DEMO_MODE=true somente no banco de demonstração.')
        try:
            inicializar_banco()
            if db.session.scalar(db.select(Usuario.id).limit(1)):
                raise click.ClickException('Já existem usuários. Nenhuma conta ou senha foi alterada.')
            senha = click.prompt('Escolha uma senha para as três contas demo (12 a 128 caracteres)', hide_input=True, confirmation_prompt=True)
            for nome, email, perfil in (
                ('Administrador Demo', 'admin@example.com', 'administrador'),
                ('Técnico Demo', 'tecnico@example.com', 'tecnico'),
                ('Solicitante Demo', 'solicitante@example.com', 'solicitante'),
            ):
                usuario = Usuario(nome=nome, email=email, perfil=perfil)
                usuario.definir_senha(senha)
                db.session.add(usuario)
            db.session.commit()
        except ValueError as error:
            raise click.ClickException(str(error)) from None
        except SQLAlchemyError:
            raise click.ClickException('Não foi possível preparar a demonstração. Confira o banco.') from None
        finally:
            db.session.rollback()
        click.echo('Contas criadas: admin@example.com, tecnico@example.com e solicitante@example.com.')
        click.echo('Use a senha escolhida. Nenhuma senha foi exibida ou definida no código.')
