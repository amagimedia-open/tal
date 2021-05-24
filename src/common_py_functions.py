import sys
import json
from datetime import datetime, timedelta

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()

def rfc3339_2_epochms(rfc3339_str):
    #https://stackoverflow.com/questions/27245488/converting-iso-8601-date-time-to-seconds-in-python
    #eg: 1984-06-02T19:05:00.000Z
    utc_dt = datetime.strptime(rfc3339_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
    return int (timestamp * 1000)

def now_2_epochms():
    #https://stackoverflow.com/questions/27245488/converting-iso-8601-date-time-to-seconds-in-python
    #eg: 1984-06-02T19:05:00.000Z
    utc_dt = datetime.utcnow()
    timestamp = (utc_dt - datetime(1970, 1, 1)).total_seconds()
    return int (timestamp * 1000)

def amagipldt_2_rfc3339(amagipldt_str):
    #eg "2018-09-17 00:30:00.000 +0000",
    (_date,_time,_utcoff) = amagipldt_str.split(" ")
    rfc3339_str = _date + "T" + _time + "Z"
    return rfc3339_str

def amagipldt_2_epochms(amagipldt_str):
    #eg "2018-09-17 00:30:00.000 +0000",
    return rfc3339_2_epochms(amagipldt_2_rfc3339(amagipldt_str))

def epochms_2_rfc3339(timestamp_ms):
    #https://stackoverflow.com/questions/27245488/converting-iso-8601-date-time-to-seconds-in-python
    us = timestamp_ms * 1000
    utc_dt = datetime(1970, 1, 1) + timedelta(microseconds=us)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def get_json_obj(filepath):
    json_obj = None
    try:
        with open(filepath) as fp:
            json_obj = json.load(fp)
    except Exception as e:
        eprint(e)

    return json_obj


