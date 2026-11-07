"""
Regression tests for the Aiken pages (/aiken-production, /aiken-unit-search,
/aiken-unfiltered-search).

Two failure modes used to surface as a bare "Internal Server Error":

1. The Aiken database rejecting the connection. This happened for real after the
   Aiken Workbench 2.2.8 update reset access for the 'manager' MySQL account, which
   broke every Aiken page at once.
2. The production query returning no rows, which crashed the Graph button inside
   seaborn (``Could not interpret value `UnitsCount` for `x```).

Both must now render the page with a flashed message. The database failure is
simulated by monkeypatching the query helpers, so nothing here touches MySQL; the
empty-result tests run against the suite's empty in-memory SQLite Aiken bind.
"""
import pytest
from sqlalchemy import exc

import website.views as views_module


ACCESS_DENIED = exc.OperationalError(
    'SELECT 1', {},
    Exception("(1045, \"Access denied for user 'manager'@'192.168.3.42' (using password: YES)\")"),
)


class _FailingQuery:
    """Stands in for a SQLAlchemy query whose execution fails at the connection."""

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        raise ACCESS_DENIED

    def paginate(self, **kwargs):
        raise ACCESS_DENIED


def _raise_access_denied(form):
    raise ACCESS_DENIED


@pytest.mark.routes
class TestAikenProductionEmptyResult:
    """The Aiken bind in the test suite has no Units, so every search is empty."""

    def test_graph_with_no_units_renders_message_not_500(self, pc_tech_client):
        response = pc_tech_client.post('/aiken-production', data={'graph': 'Graph'})
        assert response.status_code == 200
        assert b'No audited units found' in response.data

    def test_table_with_no_units_renders_message(self, pc_tech_client):
        response = pc_tech_client.post('/aiken-production', data={'table': 'Table'})
        assert response.status_code == 200
        assert b'No audited units found' in response.data

    def test_empty_message_names_the_filters(self, pc_tech_client):
        response = pc_tech_client.post('/aiken-production', data={
            'graph': 'Graph', 'start_date': '2026-11-01', 'end_date': '2026-11-05', 'active_lots': 'y',
        })
        assert response.status_code == 200
        assert b'between 2026-11-01 and 2026-11-05 in active lots' in response.data


@pytest.mark.routes
class TestAikenDatabaseFailure:
    """A rejected connection must flash the MySQL error, not 500."""

    @pytest.mark.parametrize('button', ['graph', 'table', 'download'])
    def test_production_buttons_flash_db_error(self, pc_tech_client, monkeypatch, button):
        monkeypatch.setattr(views_module, 'aiken_query', lambda form: _FailingQuery())
        response = pc_tech_client.post('/aiken-production', data={button: button.title()})
        assert response.status_code == 200
        assert b'Aiken database query failed' in response.data
        assert b'Access denied for user' in response.data

    def test_unit_search_flashes_db_error(self, pc_tech_client, monkeypatch):
        monkeypatch.setattr(views_module, 'aiken_bol_query', _raise_access_denied)
        response = pc_tech_client.post('/aiken-unit-search', data={'search': 'anything', 'table': 'Table'})
        assert response.status_code == 200
        assert b'Aiken database query failed' in response.data

    def test_unfiltered_search_flashes_db_error(self, pc_tech_client, monkeypatch):
        class FakeRazorUnfiltered:
            query = _FailingQuery()

        monkeypatch.setattr(views_module, 'RazorUnfiltered', FakeRazorUnfiltered)
        response = pc_tech_client.post('/aiken-unfiltered-search', data={'table': 'Table'})
        assert response.status_code == 200
        assert b'Aiken database query failed' in response.data
