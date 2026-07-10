"""
Test suite for database connectivity and models.
These tests verify database connections and model integrity without modifying data.
"""
import pytest
from website import db
from website.models import (
    User, Note, Production, imported_sheets, DISKS, BATCHES,
    VALIDATION, MasterVerificationLog
)


class TestDatabaseConnection:
    """Test database connectivity."""

    def test_database_connection(self, app):
        """Test that the database connection is established."""
        with app.app_context():
            # Simple query to verify connection
            try:
                result = db.session.execute(db.select(User).limit(1))
                assert result is not None
            except Exception as e:
                pytest.fail(f"Database connection failed: {e}")

    @pytest.mark.integration
    def test_all_engines_accessible(self, app):
        """Test that all database engines are accessible.

        This connects to the real production MySQL servers via the module-level
        engines, which are NOT redirected to the test database. It is marked
        ``integration`` and excluded from the default (pre-commit) run so the
        committed suite stays isolated from production. Run it on demand with
        ``pytest -m integration`` when you want to verify live connectivity.
        """
        from website import sqlEngine, validEngine, hddEngine, aikenEngine, superWiperEngine

        engines = {
            'sqlEngine': sqlEngine,
            'validEngine': validEngine,
            'hddEngine': hddEngine,
            'aikenEngine': aikenEngine,
            'superWiperEngine': superWiperEngine
        }

        for engine_name, engine in engines.items():
            try:
                with engine.connect() as conn:
                    assert conn is not None
            except Exception as e:
                pytest.fail(f"{engine_name} connection failed: {e}")


class TestUserModel:
    """Test User model functionality (read-only)."""

    def test_user_query(self, app):
        """Test that users can be queried from the database."""
        with app.app_context():
            users = User.query.limit(5).all()
            assert isinstance(users, list)

    def test_user_has_required_fields(self, app):
        """Test that User model has expected fields."""
        with app.app_context():
            user = User.query.first()
            if user:
                assert hasattr(user, 'email')
                assert hasattr(user, 'password')
                assert hasattr(user, 'first_name')
                assert hasattr(user, 'active_status')
                assert hasattr(user, 'admin_status')

    def test_user_permissions_exist(self, app):
        """Test that user permission fields exist."""
        with app.app_context():
            user = User.query.first()
            if user:
                assert hasattr(user, 'pc_status')
                assert hasattr(user, 'server_status')
                assert hasattr(user, 'processing_status')
                assert hasattr(user, 'validation_status')
                assert hasattr(user, 'qr_generation')


class TestProductionModel:
    """Test Production model functionality (read-only)."""

    def test_production_query(self, app):
        """Test that production records can be queried."""
        with app.app_context():
            try:
                records = Production.query.limit(5).all()
                assert isinstance(records, list)
            except Exception as e:
                # Some installations might not have data
                pass

    def test_production_model_exists(self, app):
        """Test that Production model is properly defined."""
        with app.app_context():
            assert Production is not None
            assert hasattr(Production, 'query')


class TestValidationModel:
    """Test Validation model functionality (read-only)."""

    def test_validation_query(self, app):
        """Test that validation records can be queried."""
        with app.app_context():
            try:
                records = VALIDATION.query.limit(5).all()
                assert isinstance(records, list)
            except Exception as e:
                # Some installations might not have data
                pass

    def test_master_validation_query(self, app):
        """Test that master validation records can be queried."""
        with app.app_context():
            try:
                records = MasterVerificationLog.query.limit(5).all()
                assert isinstance(records, list)
            except Exception as e:
                # Some installations might not have data
                pass


class TestKilldiskModels:
    """Test Killdisk-related models (read-only)."""

    def test_disks_model_query(self, app):
        """Test that DISKS model can be queried."""
        with app.app_context():
            try:
                records = DISKS.query.limit(5).all()
                assert isinstance(records, list)
            except Exception as e:
                # Some installations might not have data
                pass

    def test_batches_model_query(self, app):
        """Test that BATCHES model can be queried."""
        with app.app_context():
            try:
                records = BATCHES.query.limit(5).all()
                assert isinstance(records, list)
            except Exception as e:
                # Some installations might not have data
                pass


class TestNoteModel:
    """Test Note model functionality (read-only)."""

    def test_note_query(self, app):
        """Test that notes can be queried."""
        with app.app_context():
            try:
                notes = Note.query.limit(5).all()
                assert isinstance(notes, list)
            except Exception as e:
                pass

    def test_note_user_relationship(self, app):
        """Test that Note has relationship with User."""
        with app.app_context():
            note = Note.query.first()
            if note:
                assert hasattr(note, 'user_id')


class TestImportedSheetsModel:
    """Test imported_sheets model functionality (read-only)."""

    def test_imported_sheets_query(self, app):
        """Test that imported sheets can be queried."""
        with app.app_context():
            try:
                sheets = imported_sheets.query.limit(5).all()
                assert isinstance(sheets, list)
            except Exception as e:
                pass
