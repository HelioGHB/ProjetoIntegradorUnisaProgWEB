import os
from pathlib import Path

from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFError, CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from sigetec.models import Usuario, db

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config())
    if test_config:
        app.config.update(test_config)
    if app.config['APP_ENV'] not in ('development', 'production'):
        raise ValueError('APP_ENV deve ser development ou production.')
    production = app.config['APP_ENV'] == 'production'
    if production:
        if not app.secret_key or len(app.secret_key) < 32:
            raise ValueError('Produção exige SECRET_KEY privada com pelo menos 32 caracteres.')
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            raise ValueError('Produção exige DATABASE_URL para PostgreSQL.')
        try:
            url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
            if url.drivername not in ('postgres', 'postgresql', 'postgresql+psycopg') or url.username == 'postgres':
                raise ValueError
            if url.query.get('sslmode', 'require') not in ('require', 'verify-ca', 'verify-full'):
                raise ValueError
            app.config['SQLALCHEMY_DATABASE_URI'] = url.set(drivername='postgresql+psycopg').update_query_dict(
                {'sslmode': url.query.get('sslmode', 'require')}
            )
        except Exception:
            raise ValueError('Use PostgreSQL/Psycopg com TLS e usuário próprio da aplicação.') from None
        app.config['TRUSTED_HOSTS'] = app.config.get('TRUSTED_HOSTS') or [
            host.strip() for host in os.getenv('TRUSTED_HOSTS', os.getenv('RENDER_EXTERNAL_HOSTNAME', '')).split(',') if host.strip()
        ]
        if not app.config['TRUSTED_HOSTS'] or app.debug:
            raise ValueError('Produção exige domínio permitido e debug desativado.')
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=0, x_proto=1, x_host=0, x_port=0, x_prefix=0)
    Path(app.instance_path).mkdir(exist_ok=True)
    db.init_app(app)
    with app.app_context():
        if db.engine.dialect.name == 'sqlite':
            @event.listens_for(db.engine, 'connect')
            def sqlite_foreign_keys(connection, record):
                connection.execute('PRAGMA foreign_keys=ON')
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Entre para acessar o sistema.'
    login_manager.login_message_category = 'danger'
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if not isinstance(user_id, str) or not user_id.isdecimal() or len(user_id) > 10:
            return None
        usuario = db.session.get(Usuario, int(user_id))
        return usuario if usuario and usuario.ativo else None

    @app.errorhandler(SQLAlchemyError)
    def erro_banco(error):
        db.session.rollback()
        return render_template('erro.html', mensagem='Banco indisponível ou não preparado. Consulte as instruções do README.'), 503

    @app.errorhandler(CSRFError)
    def erro_csrf(error):
        return render_template('erro.html', mensagem='Formulário expirado ou inválido. Recarregue a página.'), 400

    @app.errorhandler(403)
    def acesso_negado(error):
        return render_template('erro.html', mensagem='Você não tem permissão para realizar esta ação.'), 403

    @app.errorhandler(404)
    def nao_encontrado(error):
        return render_template('erro.html', mensagem='Página ou chamado não encontrado.'), 404

    @app.after_request
    def cabecalhos(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Cache-Control'] = 'no-store'
        if production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    from sigetec.cli import register_cli
    from sigetec.routes import register_routes
    register_cli(app)
    register_routes(app)
    return app
