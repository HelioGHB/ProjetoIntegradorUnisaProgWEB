"""Três entidades suficientes para o fluxo acadêmico de suporte."""
from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
PERFIS = ('administrador', 'tecnico', 'solicitante')
STATUS = ('aberto', 'em_andamento', 'resolvido', 'fechado')
PRIORIDADES = ('baixa', 'media', 'alta', 'critica')


def agora():
    return datetime.now(timezone.utc)


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = (CheckConstraint("perfil IN ('administrador', 'tecnico', 'solicitante')", name='perfil_valido'),)
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.Text, nullable=False)
    perfil = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def is_active(self):
        return self.ativo

    def definir_senha(self, senha):
        if not 12 <= len(senha) <= 128:
            raise ValueError('A senha deve ter entre 12 e 128 caracteres.')
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Chamado(db.Model):
    __tablename__ = 'chamados'
    __table_args__ = (
        CheckConstraint("status IN ('aberto', 'em_andamento', 'resolvido', 'fechado')", name='status_valido'),
        CheckConstraint("prioridade IN ('baixa', 'media', 'alta', 'critica')", name='prioridade_valida'),
        CheckConstraint('length(trim(titulo)) > 0', name='titulo_obrigatorio'),
        CheckConstraint('length(trim(descricao)) > 0', name='descricao_obrigatoria'),
    )
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(10), nullable=False, default='media')
    status = db.Column(db.String(20), nullable=False, default='aberto')
    solicitante_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='RESTRICT'), nullable=False, index=True)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='RESTRICT'), index=True)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)
    atualizado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora, onupdate=agora)
    solicitante = db.relationship('Usuario', foreign_keys=[solicitante_id])
    tecnico = db.relationship('Usuario', foreign_keys=[tecnico_id])
    comentarios = db.relationship('Comentario', back_populates='chamado', order_by='Comentario.id')


class Comentario(db.Model):
    __tablename__ = 'comentarios'
    __table_args__ = (CheckConstraint('length(trim(conteudo)) > 0', name='comentario_obrigatorio'),)
    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey('chamados.id', ondelete='RESTRICT'), nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='RESTRICT'), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), nullable=False, default=agora)
    chamado = db.relationship('Chamado', back_populates='comentarios')
    usuario = db.relationship('Usuario')
