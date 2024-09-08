
from babel.dates import format_date, get_timezone

from datetime import datetime, timezone
from typing import Any, Dict


def get_date_formats(
    unix_timestamp: float, 
    locale: str = "en", 
    time_zone: str = "UTC", 
    custom_format: str = "%d. %B %Y"
) -> Dict[str, Any]:
    """
    Calculate different date formats / types.

    Args:
        unix_timestamp (float): A timestamp in seconds since 1970. Assumes UTC.
        locale (str): Locale code of language to use. Defaults to 'en'.
        time_zone (str): Timezone database name (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
        custom_format (str): strftime format specifier for the 'custom' type

    Returns:
        dict: Different date formats.
    """
    assert time_zone is not None
    assert locale is not None
    
    utc_revision_date = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
    loc_revision_date = utc_revision_date.replace(
        tzinfo=get_timezone("UTC")
    ).astimezone(get_timezone(time_zone))

    return {
        "date": format_date(loc_revision_date, format="long", locale=locale),
        "datetime": " ".join(
            [
                format_date(loc_revision_date, format="long", locale=locale),
                loc_revision_date.strftime("%H:%M:%S"),
            ]
        ),
        "iso_date": loc_revision_date.strftime("%Y-%m-%d"),
        "iso_datetime": loc_revision_date.strftime("%Y-%m-%d %H:%M:%S"),
        "timeago": '<span class="timeago" datetime="%s" locale="%s"></span>' % (loc_revision_date.isoformat(), locale),
        "custom": loc_revision_date.strftime(custom_format),
    }
    