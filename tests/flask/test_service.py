from datetime import date, timedelta

import pytest

from backend.server.routes.service import _validate_dates


@pytest.fixture
def valid_iso_formats():
    iso_start_dates = [
        "2024-01-12",
        "2022-11-03",
        "1999-08-29",
        "2000-09-14",
        "2011-04-30",
    ]
    return iso_start_dates


@pytest.fixture
def invalid_iso_formats():
    iso_start_dates = [
        "2022-13-03",
        "1999-08-32",
        "2000-02-31",
        "1231-04-39",
    ]
    return iso_start_dates


@pytest.fixture
def distant_iso_formats():
    today = date.today()
    iso_start_dates = [
        f"{today + timedelta(days=1)}",
        f"{today + timedelta(days=25)}",
        f"{today + timedelta(days=400)}",
        f"{today + timedelta(weeks=1, days=20)}",
        f"{today + timedelta(weeks=3)}",
        f"{today + timedelta(weeks=1)}",
    ]
    return iso_start_dates


def test_valid_iso_format_start_date(valid_iso_formats):
    start_dates = valid_iso_formats

    for start_date in start_dates:
        start, end, error = _validate_dates(start_date, str(date.today()))
        assert error is None


def test_invalid_iso_format_start_date(invalid_iso_formats):
    start_dates = invalid_iso_formats
    for start_date in start_dates:
        assert start_date is not None
        start, end, error = _validate_dates(start_date, str(date.today()))
        assert error is not None


def test_dates_not_synced(valid_iso_formats):
    start_dates = valid_iso_formats
    end_date = None
    for start_date in start_dates:
        end_date = date.fromisoformat(start_date) - timedelta(days=1)
        assert start_date
        assert end_date
        start, end, error = _validate_dates(start_date, str(end_date))
        assert error is not None
