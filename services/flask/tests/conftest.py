"""
Test configuration and fixtures for the PHR Flask application.

The suite runs against a disposable, in-memory SQLite database -- never the
production MySQL servers. ``website.create_app()`` accepts a ``test_config``
override (see ``website/__init__.py``); we use it to repoint the default bind
and every named bind at ``sqlite://`` so no ORM read or write can reach
production. The schema is built from the models with ``db.create_all()`` and a
small set of test users is seeded so the authenticated fixtures have accounts
to log in as.

The former module-level engines (``sqlEngine``, ``aikenEngine``, etc.) are no
longer separate hardcoded engines: ``website.get_engine(name)`` now resolves
them from the app's configured binds, so the pandas import/search/download code
paths that use them are covered by this same SQLite override and can never reach
production during a test.
"""
import pytest
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.mysql import (
    TINYTEXT, MEDIUMTEXT, LONGTEXT, TINYBLOB, MEDIUMBLOB, LONGBLOB,
)

from website import create_app, db
from website.models import User


# The models use MySQL-specific column types (TINYTEXT, LONGBLOB, ...) that the
# SQLite dialect does not know how to render, which breaks db.create_all() on
# the test database. Teach the SQLite compiler to emit a sensible equivalent for
# each. These hooks are scoped to the 'sqlite' dialect only, so production
# MySQL DDL is completely unaffected.
for _text_type in (TINYTEXT, MEDIUMTEXT, LONGTEXT):
    compiles(_text_type, "sqlite")(lambda element, compiler, **kw: "TEXT")
for _blob_type in (TINYBLOB, MEDIUMBLOB, LONGBLOB):
    compiles(_blob_type, "sqlite")(lambda element, compiler, **kw: "BLOB")


# Point the default bind AND every named bind at an isolated in-memory SQLite
# database. Each distinct ``sqlite://`` URL is its own in-memory database; that
# is fine because the models are partitioned across these binds and SQLite does
# not enforce the cross-bind foreign keys at create_all time.
TEST_CONFIG = {
    "TESTING": True,
    "WTF_CSRF_ENABLED": False,   # forms can be posted without a CSRF token
    "LOGIN_DISABLED": False,     # keep auth active so access-control tests mean something
    "SQLALCHEMY_DATABASE_URI": "sqlite://",
    "SQLALCHEMY_BINDS": {
        "hdd_db": "sqlite://",
        "r2_db": "sqlite://",
        "validation_db": "sqlite://",
        "aiken_db": "sqlite://",
        "superwiper_db": "sqlite://",
    },
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
}


def _drop_cross_bind_foreign_keys():
    """Remove foreign keys that point at a table in a different bind's metadata.

    A few models declare foreign keys across binds -- e.g.
    ``R2_Equipment_Checklist.Creator`` lives in the ``r2_db`` bind but references
    ``user.id`` in the default bind. Production MySQL tolerates these because the
    databases share a server, but SQLite's ``create_all`` resolves each foreign
    key within its own bind's metadata and cannot find the target table, so the
    schema build fails. No test depends on these constraints being enforced (and
    SQLite does not enforce foreign keys by default anyway), so we strip the
    cross-bind ones from the in-memory table definitions before creating tables.
    """
    for metadata in db.metadatas.values():
        local_tables = set(metadata.tables)
        for table in metadata.tables.values():
            for fkc in list(table.foreign_key_constraints):
                target_table = fkc.elements[0].target_fullname.rsplit(".", 1)[0]
                if target_table not in local_tables:
                    table.constraints.discard(fkc)
                    for fk in fkc.elements:
                        fk.parent.foreign_keys.discard(fk)
                        table.foreign_keys.discard(fk)


def _seed_users():
    """Seed the minimal set of users the authenticated fixtures rely on.

    Insertion order matters: the plain (non-admin) active user is created first
    so it has the lowest id and is the one ``authenticated_client`` logs in as.
    That keeps the "requires admin/permission" route tests meaningful.
    """
    from werkzeug.security import generate_password_hash

    pw = generate_password_hash("test-password")

    users = [
        # Plain active user -> authenticated_client
        User(email="active@test.local", password=pw, first_name="Active",
             active_status=True),
        # PC Tech user -> pc_tech_client
        User(email="pctech@test.local", password=pw, first_name="Tech",
             active_status=True, pc_status=True),
        # Full admin -> admin_client (every permission granted)
        User(email="admin@test.local", password=pw, first_name="Admin",
             active_status=True, admin_status=True, pc_status=True,
             network_status=True, mobile_status=True, server_status=True,
             processing_status=True, hdd_status=True, validation_status=True,
             qr_generation=True, mobile_admin_status=True),
        # Mobile admin, but NOT a full admin -> mobile_admin_client. Deliberately
        # granted ONLY mobile_admin_status (no mobile_status): users are assigned
        # either "Mobile" or "Mobile Admin", never both, so "Mobile Admin" must
        # unlock the mobile section on its own -- including the navbar menu.
        User(email="mobileadmin@test.local", password=pw, first_name="MobileAdmin",
             active_status=True, mobile_admin_status=True),
    ]
    db.session.add_all(users)
    db.session.commit()


@pytest.fixture(scope="session")
def app():
    """Create the Flask app bound to isolated SQLite databases, build the
    schema from the models, and seed test users. The databases live only for
    the duration of the test session."""
    app = create_app(test_config=TEST_CONFIG)

    with app.app_context():
        _drop_cross_bind_foreign_keys()
        db.create_all()
        _seed_users()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """A pristine, unauthenticated test client.

    This client is never mutated, so the "requires authentication" tests are
    deterministic regardless of test execution order.
    """
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """A CLI runner for the Flask application."""
    return app.test_cli_runner()


def _login_as(app, **filter_by):
    """Return a *fresh* test client authenticated as the first user matching the
    given permission flags (or an unauthenticated client if none match).

    A new client per fixture is deliberate: authenticating a shared client would
    leak the login into later tests via its cookie jar and make the
    access-control tests order-dependent.
    """
    test_client = app.test_client()
    with app.app_context():
        user = User.query.filter_by(**filter_by).first()

    if user:
        with test_client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    return test_client


@pytest.fixture(scope="function")
def authenticated_client(app):
    """A test client logged in as a plain, active (non-admin) user."""
    return _login_as(app, active_status=True)


@pytest.fixture(scope="function")
def admin_client(app):
    """A test client logged in as an active admin user."""
    return _login_as(app, admin_status=True, active_status=True)


@pytest.fixture(scope="function")
def pc_tech_client(app):
    """A test client logged in as an active PC Tech user."""
    return _login_as(app, pc_status=True, active_status=True)


@pytest.fixture(scope="function")
def mobile_admin_client(app):
    """A test client logged in as a mobile-admin user who is NOT a full admin.

    Filtering on ``admin_status=False`` is deliberate: it selects the dedicated
    mobile-admin seed user rather than the full admin (who also has the flag),
    so tests can assert the mobile-admin permission works on its own.
    """
    return _login_as(app, mobile_admin_status=True, admin_status=False,
                     active_status=True)
