from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import pyodbc
from flask_login import current_user


def EmailValidation(email):
    database = 'instance/comunidade.db'
    dados_conexao = ("Driver={SQLite3 ODBC Driver};Server=localhost;Database="+database)
    conexao = pyodbc.connect(dados_conexao)
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM usuario WHERE email='{email}'")
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return dados


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Insira a Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criar_conta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = EmailValidation(email.data)
        if usuario:
            raise ValidationError('Email já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar.')

class FormLogin(FlaskForm):
    email_login = StringField('E-mail', validators=[DataRequired(), Email()])
    senha_login = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Manter Conectado')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username_perfil = StringField('Nome de Usuário')
    email_perfil = StringField('E-mail', validators=[Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])
    curso_excel = BooleanField('Excel Impressionador')
    curso_vba = BooleanField('Vba Impressionador')
    curso_powerbi = BooleanField('PowerBi Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_ppt = BooleanField('Apresentações Impressionadoras')
    curso_sql = BooleanField('Sql Impressionador')
    botao_submit_editar = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = EmailValidation(email.data)
            if usuario:
                raise ValidationError('Já existe um usuário cadastrado para esse e-mail. Cadastre outro e-mail.')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu post aqui.', validators=[DataRequired()])
    botao_submit_post = SubmitField('Criar Post')