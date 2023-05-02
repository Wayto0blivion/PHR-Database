from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import flask_excel as excel
from simplejson import JSONEncoder
from flask_bootstrap import Bootstrap

from flask_admin import Admin, BaseView
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
DB_NAME = 'Processing_Data'

# importFolder = 'file://192.168.1.196/Root/Dustin/Testing'

sqlEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Processing_Data')
validEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Validation')
hddEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/db_killdisk')

app = Flask(__name__)


def create_app():
    app.config['SECRET_KEY'] = 'Secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Processing_Data'
    app.config['SQLALCHEMY_BINDS'] = {
        'hdd_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/db_killdisk',
        # 'r2_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Ecommerce',
        'r2_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Ecommerce',
        'validation_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Validation',
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SERVER_NAME'] = '0.0.0.0:5510'

    # initialize the flask_excel package with the current app
    excel.init_excel(app)

    # admin = Admin(name="Pandas")

    # If the below encoder is used, date objects can no longer be serialized.
    # app.json_encoder = JSONEncoder

    bootstrap = Bootstrap(app)

    db.init_app(app)

    # Setting up admin panel for Flask
    from .models import Production, imported_sheets, User
    admin = Admin(name="Pandas")
    admin.init_app(app)
    admin.add_view(ModelView(Production, db.session))
    admin.add_view(ModelView(imported_sheets, db.session))
    admin.add_view(ModelView(User, db.session))

    # Import views from python view files.
    from .views import views
    from .auth import auth
    from .testviews import testviews
    from .searchviews import searchviews

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(testviews, url_prefix='/test')
    app.register_blueprint(searchviews, url_prefix='/search')

    from .models import User, Note

    # create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app)
#         # print('Created Database!')

