from datetime import datetime, timedelta
import pytz
from Utilities.execution_log_processor import EzeAutoLogger

logger = EzeAutoLogger(__name__)


def to_app_format(posting_date_db):
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    app_format = "%d %b %Y, %I:%M %p"
    dt_str1 = datetime.strptime(str(posting_date_db), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, date_format)
    utc_date = dt_utc.replace(tzinfo=pytz.UTC)
    now_asia = utc_date.astimezone(pytz.timezone('Asia/Kolkata'))
    datetime_in_app_format = now_asia.strftime(app_format)
    return datetime_in_app_format


def from_api_to_datetime_format(api_datetime_in_ms):
    my_datetime = datetime.fromtimestamp(int(api_datetime_in_ms) / 1000)  # Apply from timestamp function
    dt_str1 = my_datetime - timedelta(hours=11, minutes=0)
    db_date_time = datetime.strptime(str(dt_str1), '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d %H:%M:%S")
    return db_date_time


def db_datetime(date_from_db):
    format1 = "%Y-%m-%dT%H:%M:%S.%f"
    date_format = "%Y-%m-%d %H:%M:%S"
    dt_str = date_from_db
    dt_str1 = datetime.strptime(str(dt_str), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, format1).strftime(date_format)
    return dt_utc


def to_chargeslip_format(posting_date_db):
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    format1 = "%Y-%m-%d, %H:%M:%S"
    dt_str = posting_date_db
    dt_str1 = datetime.strptime(str(dt_str), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, date_format)
    utc_date = dt_utc.replace(tzinfo=pytz.UTC)
    now_asia = utc_date.astimezone(pytz.timezone('Asia/Kolkata')).strftime(format1)
    date_from_db = now_asia.split(",")[0]
    time_from_db = now_asia.split(",")[1].lstrip()
    return date_from_db, time_from_db


def bump_datetime(date_from_db):
    format1 = "%Y-%m-%dT%H:%M:%S.%f"
    date_format = "%H:%M:%S"
    dt_str = date_from_db
    dt_str1 = datetime.strptime(str(dt_str), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, format1)
    orignal_date = dt_utc.strftime(date_format)
    return orignal_date


def to_portal_format(created_date_db):
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    app_format = "%d/%m/%Y, %I:%M %p"
    dt_str1 = datetime.strptime(str(created_date_db), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, date_format)
    utc_date = dt_utc.replace(tzinfo=pytz.UTC)
    now_asia = utc_date.astimezone(pytz.timezone('Asia/Kolkata'))
    datetime_in_app_format = now_asia.strftime(app_format)
    return datetime_in_app_format


def to_rearch_app_format(posting_date_db) -> str:
    """Format datetime for ReArch app display (no leading zero on hour: '2:18 PM' not '02:18 PM')."""
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    app_format = "%-d %b %Y, %-I:%M %p"
    dt_str1 = datetime.strptime(str(posting_date_db), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, date_format)
    utc_date = dt_utc.replace(tzinfo=pytz.UTC)
    now_asia = utc_date.astimezone(pytz.timezone('Asia/Kolkata'))
    return now_asia.strftime(app_format)


def to_online_refund_app_format(posting_date_db) -> str:
    """
    This method is used to format date_time according to online_refund page txns
    param: posting_date_db: str
    return: str
    """
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    app_format = "%d %b %Y, %H:%M"
    dt_str1 = datetime.strptime(str(posting_date_db), '%Y-%m-%dT%H:%M:%S.%f000').strftime("%Y-%m-%dT%H:%M:%S.%f")
    dt_utc = datetime.strptime(dt_str1, date_format)
    utc_date = dt_utc.replace(tzinfo=pytz.UTC)
    now_asia = utc_date.astimezone(pytz.timezone('Asia/Kolkata'))
    datetime_in_app_format = now_asia.strftime(app_format)
    return datetime_in_app_format