from flask import Flask
from comunidade.forms import FormLogin, FormCriarConta
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'e8bed4f3a192a783ef493bd1b82dcc5a'
if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comunidade.db'


database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# ajuste das paginas que requerem login
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar essa página.'
login_manager.login_message_category = 'alert-info'


from comunidade import routes
