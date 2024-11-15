from datetime import date, timedelta

import pytest

from backend.server.routes.service import _validate_start_date


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
        assert _validate_start_date(start_date)


def test_invalid_iso_format_start_date(invalid_iso_formats):
    start_dates = invalid_iso_formats
    for start_date in start_dates:
        assert start_date is not None
        result = _validate_start_date(start_date)
        assert result == "ERROR: INVALID"


def test_distant_iso_format_start_date(distant_iso_formats):
    start_dates = distant_iso_formats
    for start_date in start_dates:
        assert start_date is not None
        result = _validate_start_date(start_date)
        assert result == str(date.today())
