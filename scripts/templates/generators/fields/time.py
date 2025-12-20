import calendar
import random
from datetime import datetime, timedelta


def generate_date(start_date=None, end_date=None):
    """
    Generate a random date between start_date and end_date.

    Args:
        start_date: Starting date (datetime object or None for 1970-01-01)
        end_date: Ending date (datetime object or None for current date)

    Returns:
        dict: Dictionary containing 'date' (ISO format string) and 'source' (date range info)
    """
    if start_date is None:
        start_date = datetime(1970, 1, 1)

    if end_date is None:
        end_date = datetime.now()

    time_difference = (end_date - start_date).days

    random_days = random.randint(0, time_difference)

    random_date = start_date + timedelta(days=random_days)

    source = f"random/{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}"

    return {
        "data": random_date.strftime('%Y-%m-%d'),
        "source": source
    }


def year_as_number(start=1900, end=2025):
    """Generates a random year within a given range."""
    year = random.randint(start, end)
    source = f"random/{start}_to_{end}"
    return {
        "data": year,
        "source": source
    }


def month_as_number():
    """Generates a random month (1-12)."""
    month = random.randint(1, 12)
    source = "random/1_to_12"
    return {
        "data": month,
        "source": source
    }


def day_as_number(year, month):
    """
    Generates a random valid day based on the provided year and month.
    Uses calendar.monthrange to account for leap years and month lengths.
    """
    # monthrange returns (weekday of first day, number of days in month)
    last_day = calendar.monthrange(year, month)[1]
    day = random.randint(1, last_day)
    source = f"random/1_to_{last_day}"
    return {
        "data": day,
        "source": source
    }
