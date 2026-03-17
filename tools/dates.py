import datetime as dt
from typing import Optional, Union


def normalize_reference_date(
    reference_date: Optional[str],
) -> Optional[Union[dt.datetime, str]]:
    if reference_date is None:
        return None

    if isinstance(reference_date, (dt.datetime, dt.date)):
        return reference_date

    normalized = str(reference_date).strip()
    if not normalized:
        return None

    try:
        return dt.datetime.strptime(normalized, "%Y-%m-%d")
    except ValueError:
        return normalized
