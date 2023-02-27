from flask import render_template, url_for, request, flash, redirect, abort
from comunidade.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost
from comunidade import app, database, bcrypt
from comunidade.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route("/contato")
def contato():
    return render_template('contato.html')


@app.route("/usuarios")
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route("/login", methods=['GET', 'POST'])  # Liberar o método POST
def login():
    form_login = FormLogin()
    form_criar_conta = FormCriarConta()
    if request.method == 'POST' and 'botao_submit_login' in request.form and form_login.validate():
        usuario = Usuario.query.filter_by(email=form_login.email_login.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha_login.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso para o e-mail: {form_login.email_login.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for("home"))
        else:
            flash('Falha no login: Email ou Senha Incorretos', 'alert-danger')
    if request.method == 'POST' and 'botao_submit_criar_conta' in request.form and form_criar_conta.validate():
        senha_cript = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(username=form_criar_conta.username.data, email=form_criar_conta.email.data,
                          senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso para o e-mail: {form_criar_conta.email.data}', 'alert-success')
        return redirect(url_for("home"))

    return render_template('login.html', form_login=form_login, form_criar_conta=form_criar_conta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f"fotos_perfil/{current_user.foto_perfil}")
    quantidade_cursos = len(current_user.cursos.split(';')) if not current_user.cursos == 'Não Informado' else 0
    return render_template('perfil.html', foto_perfil=foto_perfil, quantidade_cursos=quantidade_cursos)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, id_usuario=current_user.id)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso.', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    file_path = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(file_path)
    return nome_arquivo


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    foto_perfil = url_for('static', filename=f"fotos_perfil/{current_user.foto_perfil}")
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email_perfil.data
        current_user.username = form.username_perfil.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = ';'.join([campo.label.text for campo in form if 'curso_' in campo.name and campo.data])
        if current_user.cursos == '':
            current_user.cursos = 'Não Informado'
        database.session.commit()
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.email_perfil.data = current_user.email
        form.username_perfil.data = current_user.username
        lista_cursos = current_user.cursos.split(';')
        for campo in form:
            if 'curso_' in campo.name:
                current_curso = [i for i in lista_cursos if campo.label.text == i]
                if current_curso:
                    campo.data = True

    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post editado com sucesso.', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso.', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)

