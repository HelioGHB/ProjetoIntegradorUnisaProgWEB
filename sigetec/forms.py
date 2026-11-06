from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import Email, InputRequired, Length

from sigetec.models import PRIORIDADES, STATUS


def limpar(value):
    return value.strip() if value else value


class LoginForm(FlaskForm):
    email = StringField('E-mail', filters=[limpar], validators=[InputRequired(), Email(), Length(max=150)])
    senha = PasswordField('Senha', validators=[InputRequired(), Length(max=128)])


class ChamadoForm(FlaskForm):
    titulo = StringField('Título', filters=[limpar], validators=[InputRequired(), Length(min=1, max=150)])
    descricao = TextAreaField('Descrição', filters=[limpar], validators=[InputRequired(), Length(min=1, max=5000)])
    prioridade = SelectField('Prioridade', choices=[(value, value.title()) for value in PRIORIDADES], default='media')


class AtualizarForm(FlaskForm):
    status = SelectField('Situação', choices=[(value, value.replace('_', ' ').title()) for value in STATUS])


class AtribuirForm(FlaskForm):
    tecnico_id = SelectField('Técnico responsável', coerce=int)


class ComentarioForm(FlaskForm):
    conteudo = TextAreaField('Comentário', filters=[limpar], validators=[InputRequired(), Length(min=1, max=3000)])
