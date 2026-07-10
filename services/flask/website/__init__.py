import os
from pathlib import Path
from urllib.parse import quote_plus

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
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
DB_NAME = 'Processing_Data'

UPLOAD_FOLDER = '/home/owner/avatars'


# Logical engine names (kept for backwards compatibility with existing call
# sites) mapped to the Flask-SQLAlchemy bind they correspond to. ``None`` is the
# default bind (Processing_Data). Code that used to import the module-level
# ``sqlEngine`` / ``hddEngine`` / ... engines now calls ``get_engine(name)``
# instead, which resolves the engine from the app's configured binds. These
# connections therefore follow the same configuration as the ORM -- including
# the test suite's isolated SQLite override -- instead of hardcoding production
# servers and credentials.
_ENGINE_BIND_KEYS = {
    'sqlEngine': None,
    'validEngine': 'validation_db',
    'hddEngine': 'hdd_db',
    'aikenEngine': 'aiken_db',
    'superWiperEngine': 'superwiper_db',
}


def get_engine(name):
    """Return the SQLAlchemy Engine for a logical connection name.

    The engine is the one Flask-SQLAlchemy manages for the matching bind, so it
    honors the active application configuration. Must be called within an
    application context (every current call site runs inside a request).
    """
    return db.engines[_ENGINE_BIND_KEYS[name]]


app = Flask(__name__)
csrf = CSRFProtect(app)
qrcode = QRcode(app)
# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'slate'


def _mysql_uri(user, password, host, database):
    """Build a pymysql connection URL, URL-encoding the password so special
    characters (``@``, ``!`` ...) survive the URL parsing."""
    return f"mysql+pymysql://{user}:{quote_plus(password)}@{host}/{database}"


def _load_local_env():
    """Populate ``os.environ`` from the repository-root ``.env`` file.

    This makes direct execution work (e.g. launching ``flask_site.py`` from an
    IDE), where nothing else loads ``.env``. Under docker-compose the variables
    are already injected via ``env_file``, so ``setdefault`` leaves those intact
    and a missing file is simply ignored. The first ``.env`` found walking up
    from this file is used, so the lookup does not depend on the current working
    directory.
    """
    for parent in Path(__file__).resolve().parents:
        env_path = parent / '.env'
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())
            return


def _require_env(*names):
    """Raise a clear error if any required environment variable is missing."""
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in the database credentials."
        )


def _production_db_config():
    """Assemble the SQLAlchemy URIs for every database from environment
    variables so that credentials are never stored in source. See .env.example.

    Database (schema) names are not secrets and stay in code; only host, user
    and password come from the environment. The primary server hosts four of
    the schemas, so its credentials are reused across those binds.
    """
    _require_env(
        'PHR_DB_HOST', 'PHR_DB_USER', 'PHR_DB_PASSWORD',
        'PHR_AIKEN_DB_HOST', 'PHR_AIKEN_DB_USER', 'PHR_AIKEN_DB_PASSWORD',
        'PHR_SUPERWIPER_DB_HOST', 'PHR_SUPERWIPER_DB_USER', 'PHR_SUPERWIPER_DB_PASSWORD',
    )
    primary = dict(
        user=os.environ['PHR_DB_USER'],
        password=os.environ['PHR_DB_PASSWORD'],
        host=os.environ['PHR_DB_HOST'],
    )
    return {
        'SQLALCHEMY_DATABASE_URI': _mysql_uri(database='Processing_Data', **primary),
        'SQLALCHEMY_BINDS': {
            'hdd_db': _mysql_uri(database='db_killdisk', **primary),
            'r2_db': _mysql_uri(database='Ecommerce', **primary),
            'validation_db': _mysql_uri(database='Validation', **primary),
            'aiken_db': _mysql_uri(
                os.environ['PHR_AIKEN_DB_USER'],
                os.environ['PHR_AIKEN_DB_PASSWORD'],
                os.environ['PHR_AIKEN_DB_HOST'],
                'awbc_db',
            ),
            'superwiper_db': _mysql_uri(
                os.environ['PHR_SUPERWIPER_DB_USER'],
                os.environ['PHR_SUPERWIPER_DB_PASSWORD'],
                os.environ['PHR_SUPERWIPER_DB_HOST'],
                'superwiper',
            ),
        },
    }


def create_app(test_config=None):
    # When running outside Docker (e.g. launching flask_site.py from an IDE),
    # load credentials from the repo-root .env. Under docker-compose these are
    # already injected via env_file, so this is a harmless no-op there. Skipped
    # for tests, which supply their own configuration.
    if not test_config:
        _load_local_env()

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'Secret!')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # app.config['SERVER_NAME'] = '0.0.0.0:5510'

    # Database configuration must be set before db.init_app(app) so the engines
    # pick it up. Callers such as the test suite provide their own config (an
    # isolated in-memory SQLite database); that branch never touches the
    # production credentials in the environment. Otherwise the real URIs are
    # assembled from environment variables.
    if test_config:
        app.config.update(test_config)
    else:
        app.config.update(_production_db_config())

    # initialize the flask_excel package with the current app
    excel.init_excel(app)

    # Initialize csrf protection
    csrf.init_app(app)

    bootstrap = Bootstrap5(app)

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





