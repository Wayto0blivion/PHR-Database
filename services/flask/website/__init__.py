from flask import Flask
from sqlalchemy import inspect
from flask_qrcode import QRcode
from flask_admin.menu import MenuLink
from flask_admin import Admin, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import BaseModelView

from flask_sqlalchemy import SQLAlchemy
from flask_statistics import Statistics
from flask_login import LoginManager
import flask_excel as excel
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
DB_NAME = 'Processing_Data'

UPLOAD_FOLDER = '/home/owner/avatars'

sqlEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/Processing_Data')
validEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/Validation')
hddEngine = db.create_engine('mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/db_killdisk')
aikenEngine = db.create_engine('mysql+pymysql://manager:powerhouse@192.168.3.247/awbc_db')

app = Flask(__name__)
csrf = CSRFProtect(app)
qrcode = QRcode(app)
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'slate'


def create_app():
    app.config['SECRET_KEY'] = 'Secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/Processing_Data'
    app.config['SQLALCHEMY_BINDS'] = {
        'hdd_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/db_killdisk',
        # 'r2_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.1.180/Ecommerce',
        'r2_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/Ecommerce',
        'validation_db': 'mysql+pymysql://sql_server:k!ndSilver83@192.168.3.243/Validation',
        'aiken_db': 'mysql+pymysql://manager:powerhouse@192.168.3.247/awbc_db',
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SERVER_NAME'] = '0.0.0.0:5510'

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # initialize the flask_excel package with the current app
    excel.init_excel(app)

    # Initialize csrf protection
    csrf.init_app(app)

    # admin = Admin(name="Pandas")

    # If the below encoder is used, date objects can no longer be serialized.
    # app.json_encoder = JSONEncoder

    bootstrap = Bootstrap(app)

    db.init_app(app)

    # Setting up admin panel for Flask
    from .models import Production, imported_sheets, User, Note, DISKS, BATCHES, VALIDATION, MasterVerificationLog
    admin = Admin(name="PHR")
    admin.init_app(app)

    # Setup ModelView functions for specific views
    class UserView(ModelView):
        column_display_pk = True
        create_modal = True
        column_editable_list = ['active_status', 'pc_status', 'server_status', 'processing_status',
                                'hdd_status', 'validation_status', 'qr_generation', 'admin_status']

    class DiskView(ModelView):
        column_display_pk = True
        column_display_foreign_keys = True
        column_default_sort = ('Finished', True)
        can_edit = False
        can_create = False
        can_delete = False

    class ValidationView(ModelView):
        column_display_pk = True
        column_default_sort = ('Date', True)
        can_create = False
        edit_modal = True

    class ProcessingView(ModelView):
        column_display_pk = True
        # column_auto_select_related = True
        # column_hide_backrefs = True
        # column_hide_backrefs = True
        # column_list = [c_attr.key for c_attr in inspect(Production).mapper.column_attrs]
        # column_searchable_list = ["sheet_id"]

    admin.add_link(MenuLink(name='Back', url='/'))

    # Adds views for specific database models to the MenuBar for Flask-Admin
    admin.add_view(ProcessingView(Production, db.session, name='Processing', category='Processing'))
    admin.add_view(ProcessingView(imported_sheets, db.session, name='Imported Sheets', category='Processing'))
    admin.add_view(DiskView(DISKS, db.session, name='Disks', category='Killdisk'))
    admin.add_view(DiskView(BATCHES, db.session, name='Batches', category='Killdisk'))
    admin.add_view(ValidationView(VALIDATION, db.session, name='Drive Validation', category='Validation'))
    admin.add_view(ValidationView(MasterVerificationLog, db.session, name='Product Validation', category='Validation'))
    admin.add_view(UserView(User, db.session, category='Users'))
    admin.add_view(ModelView(Note, db.session, category='Users'))

    # Import views from python view files.
    from .views import views
    from .auth import auth
    from .testviews import testviews
    from .searchviews import searchviews
    from .mobileviews import mobileviews

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(testviews, url_prefix='/test')
    app.register_blueprint(searchviews, url_prefix='/search')
    app.register_blueprint(mobileviews, url_prefix='/mobile')

    from .models import User, Note, Request

    # Handle statistics
    statistics = Statistics(app, db, Request)

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





