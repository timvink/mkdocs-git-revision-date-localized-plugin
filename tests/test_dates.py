import pytest
from datetime import datetime, timezone
from babel.dates import get_timezone
from babel.core import UnknownLocaleError
from mkdocs_git_revision_date_localized_plugin.dates import get_date_formats


def test_get_dates():
    # Test with default arguments
    expected_output = {
        "date": "January 1, 1970",
        "datetime": "January 1, 1970 00:00:00",
        "iso_date": "1970-01-01",
        "iso_datetime": "1970-01-01 00:00:00",
        "timeago": '<span class="timeago" datetime="1970-01-01T00:00:00+00:00" locale="en"></span>',
        "custom": "01. January 1970",
    }
    assert get_date_formats(0) == expected_output

    # Test with 4-letter locale
    new_expected_output = expected_output.copy()
    new_expected_output["timeago"] = '<span class="timeago" datetime="1970-01-01T00:00:00+00:00" locale="en_US"></span>'
    assert get_date_formats(0, locale="en_US") == new_expected_output

    # Test with different locale
    expected_output = {
        "date": "1 janvier 1970",
        "datetime": "1 janvier 1970 00:00:00",
        "iso_date": "1970-01-01",
        "iso_datetime": "1970-01-01 00:00:00",
        "timeago": '<span class="timeago" datetime="1970-01-01T00:00:00+00:00" locale="fr"></span>',
        "custom": "01. janvier 1970",
    }
    assert get_date_formats(0, locale="fr") == expected_output

    # Test with pt_BR locale
    expected_output = {
        "date": "1 de janeiro de 1970",
        "datetime": "1 de janeiro de 1970 00:00:00",
        "iso_date": "1970-01-01",
        "iso_datetime": "1970-01-01 00:00:00",
        "timeago": '<span class="timeago" datetime="1970-01-01T00:00:00+00:00" locale="pt_BR"></span>',
        "custom": "01. janeiro 1970",
    }
    assert get_date_formats(0, locale="pt_BR") == expected_output

    # Test with non-existing locale
    with pytest.raises(UnknownLocaleError):
        get_date_formats(0, locale="abcd")

    # Test with custom arguments
    expected_output = {
        "date": "January 1, 1970",
        "datetime": "January 1, 1970 00:00:00",
        "iso_date": "1970-01-01",
        "iso_datetime": "1970-01-01 00:00:00",
        "timeago": '<span class="timeago" datetime="1970-01-01T00:00:00+00:00" locale="en"></span>',
        "custom": "01. Jan 1970",
    }
    assert get_date_formats(0, locale="en", time_zone="UTC", custom_format="%d. %b %Y") == expected_output

    # Test with non-UTC timezone
    expected_output = {
        "date": "January 1, 1970",
        "datetime": "January 1, 1970 02:00:00",
        "iso_date": "1970-01-01",
        "iso_datetime": "1970-01-01 02:00:00",
        "timeago": '<span class="timeago" datetime="1970-01-01T02:00:00+01:00" locale="en"></span>',
        "custom": "01. January 1970",
    }
    loc_dt = datetime(1970, 1, 1, 1, 0, 0, tzinfo=get_timezone("Europe/Berlin"))
    unix_timestamp = loc_dt.replace(tzinfo=timezone.utc).timestamp()
    assert get_date_formats(unix_timestamp, time_zone="Europe/Berlin") == expected_output

    # Test with missing arguments
    with pytest.raises(TypeError):
        get_date_formats()  # noqa

    # Test with invalid timezone
    with pytest.raises(LookupError):
        get_date_formats(0, time_zone="Invalid/Timezone")

    # Test with more recent date
    expected_output = {
        "date": "October 15, 2023",
        "datetime": "October 15, 2023 13:32:04",
        "iso_date": "2023-10-15",
        "iso_datetime": "2023-10-15 13:32:04",
        "timeago": '<span class="timeago" datetime="2023-10-15T13:32:04+02:00" locale="en"></span>',
        "custom": "15. October 2023",
    }
    assert get_date_formats(1697369524, time_zone="Europe/Amsterdam") == expected_output

    assert get_date_formats(1582397529) == {
        "date": "February 22, 2020",
        "datetime": "February 22, 2020 18:52:09",
        "iso_date": "2020-02-22",
        "iso_datetime": "2020-02-22 18:52:09",
        "timeago": '<span class="timeago" datetime="2020-02-22T18:52:09+00:00" locale="en"></span>',
        "custom": "22. February 2020",
    }
