from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from sigetec.forms import AtribuirForm, AtualizarForm, ChamadoForm, ComentarioForm, LoginForm
from sigetec.models import Chamado, Comentario, Usuario, db

_DUMMY_HASH = generate_password_hash('nenhuma-conta-associada-a-este-valor')


def buscar_chamado(chamado_id):
    chamado = db.get_or_404(Chamado, chamado_id)
    permitido = (
        current_user.perfil == 'administrador'
        or (current_user.perfil == 'tecnico' and chamado.tecnico_id == current_user.id)
        or (current_user.perfil == 'solicitante' and chamado.solicitante_id == current_user.id)
    )
    if not permitido:
        abort(403)
    return chamado


def mostrar_erros(form):
    for erros in form.errors.values():
        for erro in erros:
            flash(erro, 'danger')


def register_routes(app):
    @app.get('/')
    def inicio():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('chamados'))
        form = LoginForm()
        if form.validate_on_submit():
            usuario = db.session.scalar(db.select(Usuario).where(Usuario.email == form.email.data.lower()))
            senha_valida = check_password_hash(usuario.senha_hash if usuario else _DUMMY_HASH, form.senha.data)
            if usuario and senha_valida and usuario.ativo:
                from flask import session
                session.clear()
                login_user(usuario)
                return redirect(url_for('chamados'))
            flash('E-mail ou senha inválidos.', 'danger')
        return render_template('login.html', form=form)

    @app.post('/logout')
    @login_required
    def logout():
        from flask import session
        logout_user()
        session.clear()
        flash('Você saiu do sistema.', 'success')
        return redirect(url_for('login'))

    @app.get('/chamados')
    @login_required
    def chamados():
        consulta = db.select(Chamado)
        if current_user.perfil == 'tecnico':
            consulta = consulta.where(Chamado.tecnico_id == current_user.id)
        elif current_user.perfil == 'solicitante':
            consulta = consulta.where(Chamado.solicitante_id == current_user.id)
        registros = db.session.scalars(consulta.order_by(Chamado.id.desc())).all()
        return render_template('chamados.html', chamados=registros)

    @app.route('/chamados/novo', methods=['GET', 'POST'])
    @login_required
    def novo_chamado():
        if current_user.perfil != 'solicitante':
            abort(403)
        form = ChamadoForm()
        if form.validate_on_submit():
            chamado = Chamado(titulo=form.titulo.data, descricao=form.descricao.data,
                              prioridade=form.prioridade.data, solicitante_id=current_user.id)
            db.session.add(chamado)
            db.session.commit()
            flash('Chamado aberto com sucesso.', 'success')
            return redirect(url_for('detalhe_chamado', chamado_id=chamado.id))
        return render_template('novo_chamado.html', form=form)

    @app.get('/chamados/<int:chamado_id>')
    @login_required
    def detalhe_chamado(chamado_id):
        chamado = buscar_chamado(chamado_id)
        atribuicao = AtribuirForm(tecnico_id=chamado.tecnico_id or 0)
        atribuicao.tecnico_id.choices = [(0, 'Não atribuído')] + [
            (usuario.id, usuario.nome) for usuario in db.session.scalars(
                db.select(Usuario).where(Usuario.perfil == 'tecnico', Usuario.ativo.is_(True)).order_by(Usuario.nome)
            )
        ]
        return render_template('detalhe_chamado.html', chamado=chamado,
                               atribuicao=atribuicao, atualizacao=AtualizarForm(status=chamado.status),
                               comentario=ComentarioForm())

    @app.post('/chamados/<int:chamado_id>/atribuir')
    @login_required
    def atribuir_chamado(chamado_id):
        if current_user.perfil != 'administrador':
            abort(403)
        chamado = buscar_chamado(chamado_id)
        form = AtribuirForm()
        form.tecnico_id.choices = [(0, 'Não atribuído')] + [
            (usuario.id, usuario.nome) for usuario in db.session.scalars(
                db.select(Usuario).where(Usuario.perfil == 'tecnico', Usuario.ativo.is_(True))
            )
        ]
        if form.validate_on_submit():
            chamado.tecnico_id = form.tecnico_id.data or None
            db.session.commit()
            flash('Responsável atualizado.', 'success')
        else:
            mostrar_erros(form)
        return redirect(url_for('detalhe_chamado', chamado_id=chamado.id))

    @app.post('/chamados/<int:chamado_id>/status')
    @login_required
    def atualizar_chamado(chamado_id):
        chamado = buscar_chamado(chamado_id)
        if current_user.perfil not in ('administrador', 'tecnico'):
            abort(403)
        form = AtualizarForm()
        if form.validate_on_submit():
            if chamado.status == 'fechado' and form.status.data != 'fechado' and current_user.perfil != 'administrador':
                abort(403)
            chamado.status = form.status.data
            db.session.commit()
            flash('Situação atualizada.', 'success')
        else:
            mostrar_erros(form)
        return redirect(url_for('detalhe_chamado', chamado_id=chamado.id))

    @app.post('/chamados/<int:chamado_id>/comentar')
    @login_required
    def comentar_chamado(chamado_id):
        chamado = buscar_chamado(chamado_id)
        form = ComentarioForm()
        if form.validate_on_submit():
            db.session.add(Comentario(chamado_id=chamado.id, usuario_id=current_user.id, conteudo=form.conteudo.data))
            db.session.commit()
            flash('Comentário registrado.', 'success')
        else:
            mostrar_erros(form)
        return redirect(url_for('detalhe_chamado', chamado_id=chamado.id))

    @app.get('/healthz')
    def healthz():
        try:
            db.session.execute(text('SELECT 1'))
            db.session.execute(db.select(Usuario.id).limit(1))
        except SQLAlchemyError:
            db.session.rollback()
            return {'status': 'indisponivel'}, 503
        return {'status': 'ok'}
