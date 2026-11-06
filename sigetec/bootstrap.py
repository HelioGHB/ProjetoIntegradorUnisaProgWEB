"""Inicialização explícita e repetível; nunca apaga ou redefine dados."""
import click
from email_validator import EmailNotValidError, validate_email
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from sigetec.models import Usuario, db


def inicializar_banco(connection, criar=True):
    inspector = inspect(connection)
    existentes = set(inspector.get_table_names())
    esperadas = set(db.metadata.tables)
    if existentes:
        estrutura_igual = existentes == esperadas and all(
            {coluna['name'] for coluna in inspector.get_columns(nome)}
            == set(db.metadata.tables[nome].columns.keys()) for nome in esperadas
        )
        if not estrutura_igual:
            raise click.ClickException('O banco já contém outra estrutura; nenhum dado foi alterado. Revise o esquema antes de continuar.')
        return False
    if not criar:
        raise click.ClickException('Banco sem tabelas. Habilite INIT_DB_ON_START=true ou execute init-db primeiro.')
    db.metadata.create_all(bind=connection)
    return True


def bloquear_inicializacao(connection):
    # Evita disputa entre duas instâncias em um deploy PostgreSQL.
    # O bloqueio é liberado pelo próprio banco ao concluir a transação.
    if connection.dialect.name == 'postgresql':
        connection.execute(text("SET LOCAL lock_timeout = '10s'"))
        connection.execute(text('SELECT pg_advisory_xact_lock(814230917)'))


def validar_administrador(nome, email, senha):
    nome = (nome or '').strip()
    if not 1 <= len(nome) <= 120:
        raise click.ClickException('Informe um nome de administrador com 1 a 120 caracteres.')
    try:
        email = validate_email((email or '').strip(), check_deliverability=False).normalized.lower()
    except EmailNotValidError:
        raise click.ClickException('Informe um e-mail válido para o administrador.') from None
    if len(email) > 150:
        raise click.ClickException('O e-mail deve ter até 150 caracteres.')
    if not senha or not 12 <= len(senha) <= 128:
        raise click.ClickException('A senha do administrador deve ter entre 12 e 128 caracteres.')
    return nome, email, senha


def criar_administrador(connection, dados):
    nome, email, senha = dados
    with Session(bind=connection) as session:
        if session.scalar(db.select(Usuario.id).where(Usuario.perfil == 'administrador').limit(1)):
            return False
        if session.scalar(db.select(Usuario.id).where(Usuario.email == email)):
            raise click.ClickException('O e-mail informado já pertence a outro usuário. Nenhuma conta foi alterada.')
        usuario = Usuario(nome=nome, email=email, perfil='administrador', ativo=True)
        usuario.definir_senha(senha)
        session.add(usuario)
        # O commit da conexão externa continua sob controle de engine.begin().
        session.commit()
    return True


def inicializar_deploy(app):
    init_db = app.config.get('INIT_DB_ON_START', False)
    init_admin = app.config.get('CREATE_ADMIN_ON_START', False)
    if not init_db and not init_admin:
        return False, False
    dados = None
    if init_admin:
        # Valida tudo antes de qualquer DDL ou escrita no banco.
        dados = validar_administrador(
            app.config.get('BOOTSTRAP_ADMIN_NAME'),
            app.config.get('BOOTSTRAP_ADMIN_EMAIL'),
            app.config.get('BOOTSTRAP_ADMIN_PASSWORD'),
        )
    with db.engine.begin() as connection:
        bloquear_inicializacao(connection)
        criado = inicializar_banco(connection, criar=init_db)
        admin_criado = criar_administrador(connection, dados) if init_admin else False
    return criado, admin_criado
