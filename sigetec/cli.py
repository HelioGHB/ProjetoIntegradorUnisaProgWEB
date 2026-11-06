"""Inicialização explícita, sem apagar ou recriar banco existente."""
import click
from sqlalchemy.exc import SQLAlchemyError

from sigetec.models import Usuario, db
from sigetec.bootstrap import (
    bloquear_inicializacao, criar_administrador, inicializar_banco,
    inicializar_deploy, validar_administrador,
)


def register_cli(app):
    @app.cli.command('init-db')
    def init_db():
        """Cria as três tabelas apenas se o banco estiver vazio."""
        try:
            with db.engine.begin() as connection:
                bloquear_inicializacao(connection)
                criado = inicializar_banco(connection)
        except SQLAlchemyError:
            raise click.ClickException('Não foi possível inicializar o banco. Confira a configuração.') from None
        click.echo('Banco inicializado.' if criado else 'Banco já inicializado; nenhuma alteração realizada.')

    @app.cli.command('preparar-demo')
    def preparar_demo():
        """Prepara o banco e três contas fictícias com senha escolhida no terminal."""
        if app.config['APP_ENV'] == 'production' and not app.config.get('DEMO_MODE'):
            raise click.ClickException('Em produção, habilite DEMO_MODE=true somente no banco de demonstração.')
        try:
            with db.engine.begin() as connection:
                bloquear_inicializacao(connection)
                inicializar_banco(connection)
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

    @app.cli.command('criar-admin')
    def criar_admin():
        """Cria somente o primeiro administrador, com senha digitada de forma oculta."""
        dados = validar_administrador(
            click.prompt('Nome'), click.prompt('E-mail'),
            click.prompt('Senha (12 a 128 caracteres)', hide_input=True, confirmation_prompt=True),
        )
        try:
            with db.engine.begin() as connection:
                bloquear_inicializacao(connection)
                inicializar_banco(connection, criar=False)
                criado = criar_administrador(connection, dados)
        except SQLAlchemyError:
            raise click.ClickException('Não foi possível criar o administrador. Confira o banco; detalhes privados foram omitidos.') from None
        click.echo('Administrador criado.' if criado else 'Administrador já existente; nenhuma conta ou senha foi alterada.')

    @app.cli.command('inicializar-deploy')
    def inicializar_deploy_command():
        """Inicializa opcionalmente por variáveis privadas, sem prompts ou rotas web."""
        if not app.config.get('INIT_DB_ON_START') and not app.config.get('CREATE_ADMIN_ON_START'):
            click.echo('Inicialização no start desativada; nenhuma alteração no banco.')
            return
        try:
            tabelas, administrador = inicializar_deploy(app)
        except SQLAlchemyError:
            raise click.ClickException('Inicialização não concluída. Confira conexão, permissões e esquema do banco; detalhes privados foram omitidos.') from None
        click.echo('Tabelas criadas.' if tabelas else 'Tabelas já existentes; estrutura preservada.')
        if app.config.get('CREATE_ADMIN_ON_START'):
            click.echo('Administrador criado.' if administrador else 'Administrador já existente; senha preservada.')
