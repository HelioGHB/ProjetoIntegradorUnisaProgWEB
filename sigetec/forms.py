from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SelectChoice, SelectField, StringField, TextAreaField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from sigetec.models import PRIORIDADES, STATUS


def limpar(value):
    return value.strip() if value else value


class LoginForm(FlaskForm):
    email = EmailField('E-mail', filters=[limpar], validators=[InputRequired(message='Informe o e-mail.'), Email(message='Informe um e-mail válido.'), Length(max=150)], render_kw={'autocomplete': 'username'})
    senha = PasswordField('Senha', validators=[InputRequired(message='Informe a senha.'), Length(max=128)], render_kw={'autocomplete': 'current-password'})


class ChamadoForm(FlaskForm):
    titulo = StringField('Título', filters=[limpar], validators=[InputRequired(), Length(min=1, max=150)])
    descricao = TextAreaField('Descrição', filters=[limpar], validators=[InputRequired(), Length(min=1, max=5000)])
    prioridade = SelectField('Prioridade', choices=[SelectChoice(value, value.title()) for value in PRIORIDADES], default='media')


class AtualizarForm(FlaskForm):
    status = SelectField('Situação', choices=[SelectChoice(value, value.replace('_', ' ').title()) for value in STATUS])


class AtribuirForm(FlaskForm):
    tecnico_id = SelectField('Técnico responsável', coerce=int)


class ComentarioForm(FlaskForm):
    conteudo = TextAreaField('Comentário', filters=[limpar], validators=[InputRequired(), Length(min=1, max=3000)])


class UsuarioForm(FlaskForm):
    nome = StringField('Nome', filters=[limpar], validators=[
        InputRequired(message='Informe o nome.'),
        Length(min=1, max=120, message='O nome deve ter entre 1 e 120 caracteres.'),
    ])
    email = EmailField('E-mail', filters=[limpar], validators=[
        InputRequired(message='Informe o e-mail.'), Email(message='Informe um e-mail válido.'),
        Length(max=150, message='O e-mail deve ter até 150 caracteres.'),
    ], render_kw={'autocomplete': 'off'})
    perfil = SelectField('Perfil', choices=[
        SelectChoice('solicitante', 'Solicitante'), SelectChoice('tecnico', 'Técnico'),
    ])
    senha = PasswordField('Senha inicial', validators=[
        InputRequired(message='Informe uma senha inicial.'),
        Length(min=12, max=128, message='A senha deve ter entre 12 e 128 caracteres.'),
    ], render_kw={'autocomplete': 'new-password'})
    confirmar_senha = PasswordField('Confirmar senha', validators=[
        InputRequired(message='Confirme a senha.'),
        EqualTo('senha', message='As senhas devem ser iguais.'),
    ], render_kw={'autocomplete': 'new-password'})
