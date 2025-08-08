import re
from datetime import datetime


def validate_date_format(date_str: str) -> bool:
    """Valida que la fecha tenga formato DD-MM-YYYY"""
    if not isinstance(date_str, str):
        return False

    # Regex para formato DD-MM-YYYY
    pattern = r"^(\d{2})-(\d{2})-(\d{4})$"
    match = re.match(pattern, date_str)

    if not match:
        return False

    try:
        # Validar que sea una fecha real
        day, month, year = match.groups()
        datetime(int(year), int(month), int(day))
        return True
    except ValueError:
        return False
