import re
import datetime


def parse_cdms_date(val):
    # dates from CDMS are in UTC
    parsed_val = int(re.search('/Date\(([-+]?\d+)\)/', val).group(1))
    parsed_val = datetime.datetime.fromtimestamp(parsed_val / 1000)
    return parsed_val.replace(tzinfo=datetime.timezone.utc)
