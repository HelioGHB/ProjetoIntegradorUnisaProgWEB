"""Capturas reais em navegador, com SQLite temporário e dados fictícios.

Ferramenta opcional: instalar Playwright e Chromium conforme docs/apresentacao.md.
Nunca carrega senhas de contas online nem conecta ao PostgreSQL hospedado.
"""
from datetime import datetime, timezone
import logging
from pathlib import Path
import secrets
import sys
import tempfile
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from sigetec import create_app
from sigetec.models import Chamado, Comentario, Usuario, db


def main():
    output = ROOT / 'docs' / 'images'
    output.mkdir(parents=True, exist_ok=True)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    senha = secrets.token_hex(24)
    with tempfile.TemporaryDirectory(prefix='sigetec-captura-') as temporary:
        app = create_app({
            'TESTING': True, 'APP_ENV': 'development',
            'SECRET_KEY': secrets.token_hex(32),
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{Path(temporary) / "demo.sqlite3"}',
            'SESSION_COOKIE_SECURE': False,
            'INIT_DB_ON_START': False, 'CREATE_ADMIN_ON_START': False,
            'TRUSTED_HOSTS': ['127.0.0.1'],
        })
        with app.app_context():
            db.create_all()
            admin = Usuario(nome='Administrador Demo', email='admin.demo@example.com', perfil='administrador')
            tecnico = Usuario(nome='Lucas Demo', email='tecnico.demo@example.com', perfil='tecnico')
            professor = Usuario(nome='Ana Demo', email='professor.demo@example.com', perfil='solicitante')
            for usuario in (admin, tecnico, professor):
                usuario.definir_senha(senha)
                db.session.add(usuario)
            db.session.flush()
            aberto = datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc)
            resolvido = Chamado(
                titulo='Computador sem acesso à rede',
                descricao='O computador do laboratório não consegue acessar a rede.\nOs demais equipamentos estão funcionando normalmente.',
                prioridade='alta', status='resolvido', solicitante=professor, tecnico=tecnico,
                criado_em=aberto, atualizado_em=aberto.replace(hour=13),
            )
            db.session.add_all([
                resolvido,
                Chamado(titulo='Instalação de aplicativo acadêmico', descricao='Instalar a ferramenta para a aula prática.', prioridade='media', status='em_andamento', solicitante=professor, tecnico=tecnico, criado_em=aberto, atualizado_em=aberto),
                Chamado(titulo='Impressora não imprime documentos', descricao='A impressora do laboratório está com a fila parada.', prioridade='baixa', status='aberto', solicitante=professor, criado_em=aberto, atualizado_em=aberto),
            ])
            db.session.add_all([
                Comentario(chamado=resolvido, usuario=tecnico, conteudo='Cabo de rede substituído. Conectividade e acesso aos sistemas testados com sucesso.', criado_em=aberto.replace(minute=40)),
                Comentario(chamado=resolvido, usuario=professor, conteudo='A conexão voltou a funcionar. Obrigada pelo atendimento!', criado_em=aberto.replace(hour=13)),
            ])
            db.session.commit()
            chamado_id = resolvido.id
        server = make_server('127.0.0.1', 0, app, threaded=True)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                context = browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1, locale='pt-BR')
                page = context.new_page()
                page.goto(base + '/login')
                page.get_by_role('heading', name='Entrar no SIGETEC').wait_for()
                page.screenshot(path=str(output / '01-login.png'), full_page=True)
                page.get_by_label('E-mail').fill('admin.demo@example.com')
                page.get_by_label('Senha', exact=True).fill(senha)
                page.get_by_role('button', name='Entrar', exact=True).click()
                page.wait_for_url(base + '/chamados')
                page.get_by_role('link', name='Computador sem acesso à rede').wait_for()
                page.screenshot(path=str(output / '02-chamados.png'), full_page=True)
                page.get_by_role('button', name='Sair', exact=True).click()
                page.wait_for_url(base + '/login')
                page.get_by_label('E-mail').fill('professor.demo@example.com')
                page.get_by_label('Senha', exact=True).fill(senha)
                page.get_by_role('button', name='Entrar', exact=True).click()
                page.wait_for_url(base + '/chamados')
                page.goto(base + f'/chamados/{chamado_id}')
                page.get_by_text('Cabo de rede substituído.', exact=False).wait_for()
                page.screenshot(path=str(output / '03-atendimento.png'), full_page=True)
                browser.close()
            print('Três capturas geradas em docs/images, com dados fictícios e sem credenciais.')
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()
            with app.app_context():
                db.session.remove()
                db.engine.dispose()


if __name__ == '__main__':
    main()
